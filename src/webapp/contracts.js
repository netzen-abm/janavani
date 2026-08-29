export const CASE_SCHEMA_VERSION = "1.0";

export function createCasePayload({ title, description, location = null, category = null }) {
  return {
    schema_version: CASE_SCHEMA_VERSION,
    title: String(title).trim(),
    description: String(description).trim(),
    location: location == null ? null : String(location).trim(),
    category: category == null ? null : String(category).trim(),
  };
}

export function capabilityRequest(capability, operation, input = {}) {
  return {
    capability,
    operation,
    input,
    schema_version: CASE_SCHEMA_VERSION,
  };
}
