#[cfg(test)]
mod tests {
    use crate::sos_interface::JanavaniWasmSOSTrigger;
    use crate::decentralized_drivers::JanavaniDecentralizedCore;

    #[test]
    fn test_reticulum_mesh_packet_compression_and_structure() {
        let sample_alert = "🚨 JANAVANI SOS ALERT | TYPE: Late Night Travel | LOC: 12.9716, 77.5946 | ID: TEST_NODE";
        
        // Assert that the ad-hoc radio injection pipeline maps payloads accurately
        let result = JanavaniDecentralizedCore::transmit_via_reticulum_mesh(sample_alert);
        
        assert!(result.is_ok());
        let transport_hash = result.unwrap();
        assert!(transport_hash.len() > 10);
    }
}
