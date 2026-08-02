Update docs: BLE mesh + Noise protocol usage notes

- services/ble_mesh.py : prototype BLE mesh helpers using bleak. Mobile apps should
  implement native mesh features and conform to the packet format defined in
  services/binary_protocol.py.
- services/noise_protocol.py : helper wrappers around a Noise protocol implementation
  for session establishment and message encryption/decryption.

Usage example (high-level):
1. Serialize rating JSON to bytes.
2. Create a Noise initiator session with a peer and perform handshake over BLE
   (exchange handshake packets using ble_mesh send/receive functions).
3. Encrypt the rating payload with the established Noise session and pack it using
   services/binary_protocol.pack_packet(MSG_TYPE_RATING, encrypted_payload).
4. Publish the packet via publish_via_ble_mesh().
5. Optionally, when internet is available, also publish the CID via Nostr using
   services/nostr_client.publish_nostr_event to achieve global reach.
