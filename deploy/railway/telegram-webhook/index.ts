import { timingSafeEqual } from "node:crypto";

const MAX_BODY_BYTES = 256 * 1024;
const seenUpdates = new Map<number, number>();
const inFlightUpdates = new Map<number, Promise<void>>();
let lastWebhookRegistrationAt = 0;
let registrationInFlight: Promise<void> | null = null;

function env(name: string): string {
  return (Bun.env[name] ?? "").trim();
}

function json(data: unknown, status = 200): Response {
  return Response.json(data, {
    status,
    headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" },
  });
}

function secretMatches(actual: string | null, expected: string): boolean {
  if (!actual || !expected) return false;
  const a = Buffer.from(actual, "utf8");
  const b = Buffer.from(expected, "utf8");
  return a.length === b.length && timingSafeEqual(a, b);
}

async function registerWebhookIfConfigured(): Promise<void> {
  const token = env("TELEGRAM_BOT_TOKEN");
  const url = env("TELEGRAM_WEBHOOK_URL");
  const secret = env("TELEGRAM_WEBHOOK_SECRET");
  if (!token || !url || !secret) return;
  if (Date.now() - lastWebhookRegistrationAt < 30_000) return;
  if (registrationInFlight) return registrationInFlight;

  registrationInFlight = (async () => {
    const response = await fetch(`https://api.telegram.org/bot${token}/setWebhook`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        url,
        secret_token: secret,
        allowed_updates: ["message", "edited_message"],
        drop_pending_updates: false,
        max_connections: 10,
      }),
      signal: AbortSignal.timeout(5_000),
    });
    const result = await response.json() as { ok?: boolean; description?: string };
    if (!response.ok || result.ok !== true) {
      // Keep logs free of the bot token, citizen payloads, and the secret header.
      console.error("telegram_webhook_registration_failed", {
        status: response.status,
        reason: String(result.description ?? "Telegram API rejected setWebhook").slice(0, 140),
      });
      throw new Error("telegram_webhook_registration_failed");
    }
    lastWebhookRegistrationAt = Date.now();
    console.info("telegram_webhook_registered");
  })();

  try {
    await registrationInFlight;
  } finally {
    registrationInFlight = null;
  }
}

function replyFor(text: string): string {
  const command = text.trim().split(/\s+/, 1)[0].toLowerCase().split("@", 1)[0];
  if (command === "/start") {
    return [
      "🇮🇳 Welcome to Janavani — The Infrastructure of Citizen Voice.",
      "",
      "I can guide you toward preparing a civic request.",
      "",
      "/complaint — prepare a public-service complaint",
      "/rti — understand an RTI request",
      "/help — available commands",
      "",
      "Privacy: please do not send Aadhaar numbers, passwords, bank details, medical records, or other sensitive personal information.",
      "",
      "This is an early webhook MVP. It does not yet save, file, or track a real case."
    ].join("\n");
  }
  if (command === "/help") {
    return "Janavani commands:\n/start — welcome and guidance\n/complaint — complaint preparation\n/rti — RTI guidance\n/help — this menu\n\nThis demo does not submit requests to public authorities.";
  }
  if (command === "/complaint") {
    return "To prepare a useful complaint, note the public service or issue, the general area, when it began, and the remedy requested. Do not include sensitive identifiers.\n\nThis MVP can provide guidance only; it does not yet save or submit a complaint.";
  }
  if (command === "/rti") {
    return "An RTI request should identify the public authority, the records or information sought, and a clear time period where relevant. Ask for existing records rather than opinions.\n\nThis MVP provides guidance only; it does not file an RTI application.";
  }
  if (!text.trim()) return "";
  return "I received your message, but this early MVP does not yet create or submit a civic case. Use /complaint or /rti for guidance. Please avoid sending sensitive personal information.";
}

async function sendTelegramMessage(chatId: number | string, text: string): Promise<void> {
  const token = env("TELEGRAM_BOT_TOKEN");
  if (!token) throw new Error("telegram_bot_token_not_configured");
  const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text: text.slice(0, 3900), disable_web_page_preview: true }),
    signal: AbortSignal.timeout(8_000),
  });
  const result = await response.json() as { ok?: boolean };
  if (!response.ok || result.ok !== true) throw new Error("telegram_send_message_failed");
}

async function readBoundedBody(request: Request): Promise<Uint8Array> {
  const declaredLength = Number(request.headers.get("content-length") ?? "0");
  if (Number.isFinite(declaredLength) && declaredLength > MAX_BODY_BYTES) {
    throw new Error("body_too_large");
  }
  if (!request.body) return new Uint8Array();
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > MAX_BODY_BYTES) {
        await reader.cancel();
        throw new Error("body_too_large");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const body = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return body;
}

Bun.serve({
  port: Number(Bun.env.PORT ?? "3000"),
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/livez") {
      return json({ status: "alive", service: "janavani-telegram-webhook" });
    }

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/health" || url.pathname === "/readyz")) {
      const botConfigured = Boolean(env("TELEGRAM_BOT_TOKEN"));
      const webhookConfigured = Boolean(env("TELEGRAM_WEBHOOK_URL") && env("TELEGRAM_WEBHOOK_SECRET"));
      if (!botConfigured || !webhookConfigured) {
        return json({
          status: "not_ready",
          service: "janavani-telegram-webhook",
          botConfigured,
          webhookConfigured,
          note: "Add TELEGRAM_BOT_TOKEN in Railway to activate the bot.",
        }, 503);
      }
      try {
        await registerWebhookIfConfigured();
      } catch {
        return json({
          status: "degraded",
          service: "janavani-telegram-webhook",
          botConfigured,
          webhookConfigured,
          note: "Telegram webhook registration failed; inspect sanitized runtime logs.",
        }, 503);
      }
      return json({
        status: "ready",
        service: "janavani-telegram-webhook",
        botConfigured,
        webhookConfigured,
      });
    }

    if (request.method !== "POST" || url.pathname !== "/telegram/webhook") {
      return json({ error: "not_found" }, 404);
    }

    if (!secretMatches(request.headers.get("x-telegram-bot-api-secret-token"), env("TELEGRAM_WEBHOOK_SECRET"))) {
      return json({ error: "unauthorized" }, 403);
    }

    let payload: any;
    try {
      const bytes = await readBoundedBody(request);
      payload = JSON.parse(new TextDecoder().decode(bytes));
    } catch (error) {
      return json({ error: error instanceof Error && error.message === "body_too_large" ? "payload_too_large" : "invalid_json" },
        error instanceof Error && error.message === "body_too_large" ? 413 : 400);
    }

    if (!payload || typeof payload !== "object" || Array.isArray(payload) ||
        !Number.isSafeInteger(payload.update_id) || payload.update_id < 0) {
      return json({ error: "invalid_telegram_update" }, 400);
    }

    // Process-local deduplication prevents concurrent duplicate replies in a warm instance.
    // Durable cross-restart idempotency requires the canonical encrypted PostgreSQL inbox.
    const updateId = payload.update_id as number;
    if (seenUpdates.has(updateId)) return json({ status: "duplicate_acknowledged" });
    const existing = inFlightUpdates.get(updateId);
    if (existing) {
      try {
        await existing;
        return json({ status: "duplicate_acknowledged" });
      } catch {
        return json({ error: "temporarily_unavailable" }, 503);
      }
    }

    const message = payload.message ?? payload.edited_message;
    const chatId = message?.chat?.id;
    const text = typeof message?.text === "string" ? message.text : "";
    const processing = (async () => {
      if ((typeof chatId === "number" || typeof chatId === "string") && text) {
        const reply = replyFor(text);
        if (reply) await sendTelegramMessage(chatId, reply);
      }
    })();
    inFlightUpdates.set(updateId, processing);

    try {
      await processing;
      seenUpdates.set(updateId, Date.now());
      if (seenUpdates.size > 5000) {
        const oldest = seenUpdates.keys().next().value;
        if (oldest !== undefined) seenUpdates.delete(oldest);
      }
      return json({ status: "accepted" });
    } catch {
      // Avoid logging citizen text, chat IDs, bot tokens, or Telegram payloads.
      console.error("telegram_update_processing_failed", { updateId });
      return json({ error: "temporarily_unavailable" }, 503);
    } finally {
      if (inFlightUpdates.get(updateId) === processing) inFlightUpdates.delete(updateId);
    }
  },
});

console.info("janavani_telegram_webhook_started");