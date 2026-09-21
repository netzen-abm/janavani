use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub enum AccountabilityTarget {
    IasOfficer, IpsOfficer, IfsOfficer, IrsOfficer,
    Bdo, Collector, Sp, ChiefSecretary, PrincipalSecretary,
    LsgdBody, CenterGovtDepartment, StateGovtDepartment,
    GovtHospital, GovtSchool, GovtCollege, PoliceStation,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct PerformanceMetric {
    pub target_type: AccountabilityTarget,
    pub target_identifier_name_or_code: String,
    pub public_handling_rating: u8,   // 1 to 5
    pub resolution_velocity_rating: u8, // 1 to 5
    pub integrity_and_attitude_rating: u8, // 1 to 5
    pub office_cleanliness_rating: u8,   // 1 to 5
    pub public_commentary: String,
}
