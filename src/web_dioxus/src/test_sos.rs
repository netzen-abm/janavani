#[cfg(test)]
mod tests {
    use crate::decentralized_drivers::JanavaniDecentralizedCore;

    #[test]
    fn test_reticulum_mesh_is_not_reported_as_verified_without_adapter() {
        let sample_alert =
            "🚨 JANAVANI SOS ALERT | TYPE: Late Night Travel | LOC: 12.9716, 77.5946 | ID: TEST_NODE";

        let result = JanavaniDecentralizedCore::transmit_via_reticulum_mesh(sample_alert);

        assert!(result.is_err());
        let error = result.unwrap_err();
        assert_eq!(error.capability, "reticulum");
    }
}
