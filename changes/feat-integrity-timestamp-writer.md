type: Added
area: 3
requirements: FR-VLT-007, FR-VFY-005
summary: Add format_timestamp and parse_timestamp (Python and JavaScript) for the hashed-record time form YYYY-MM-DDTHH:MM:SS+HH:MM, with generated vectors in test-vectors/integrity/timestamp.json (issue #62). The written form is unchanged; Z, missing offset, fractional seconds and -00:00 are rejected.
