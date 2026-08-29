/**
 * Recovery policy for user-controlled local vault keys.
 *
 * Janavani never uploads raw vault keys, recovery passphrases, or personal
 * Case/Evidence data for recovery. This module only defines local policy.
 */

export const RECOVERY_POLICY_VERSION = 1;

export const RECOVERY_MODES = Object.freeze({
  PASSPHRASE: "passphrase",
  USER_MANAGED_EXPORT: "user_managed_export",
});

export function validateRecoveryChoice({ mode, passphrase } = {}) {
  if (!Object.values(RECOVERY_MODES).includes(mode)) {
    throw new Error("Unsupported recovery mode");
  }
  if (mode === RECOVERY_MODES.PASSPHRASE && (typeof passphrase !== "string" || passphrase.length < 12)) {
    throw new Error("Recovery passphrase must be at least 12 characters");
  }
  return { version: RECOVERY_POLICY_VERSION, mode };
}

export function recoveryMustRemainLocal() {
  return Object.freeze({
    upload_key: false,
    upload_passphrase: false,
    upload_personal_data: false,
  });
}
