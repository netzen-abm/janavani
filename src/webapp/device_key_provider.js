/**
 * Provider-neutral device key boundary.
 *
 * The Web implementation deliberately keeps the non-exportable CryptoKey only
 * in the current client session. A durable device/recovery provider can later
 * implement this interface without changing Case/Evidence capabilities.
 */

export class DeviceKeyProvider {
  async create() { throw new Error("Not implemented"); }
  async unlock() { throw new Error("Not implemented"); }
  async rotate() { throw new Error("Not implemented"); }
  async destroy() { throw new Error("Not implemented"); }
}

export class WebSessionKeyProvider extends DeviceKeyProvider {
  constructor(createKey) {
    super();
    this.createKey = createKey;
    this.key = null;
  }

  async create() {
    this.key = await this.createKey();
    return this.key;
  }

  async unlock() {
    if (!this.key) throw new Error("Device key is not unlocked in this session");
    return this.key;
  }

  async rotate() {
    this.key = await this.createKey();
    return this.key;
  }

  async destroy() {
    this.key = null;
  }
}
