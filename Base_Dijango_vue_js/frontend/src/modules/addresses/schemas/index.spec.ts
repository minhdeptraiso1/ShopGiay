import { addressValuesSchema } from ".";

describe("addressValuesSchema", () => {
  it("validates a complete Vietnamese delivery address", () => {
    expect(
      addressValuesSchema.safeParse({
        recipientName: "Nguyễn Văn A",
        phoneNumber: "0901234567",
        province: "Hà Nội",
        district: "Ba Đình",
        ward: "Điện Biên",
        streetAddress: "12 Đường Độc Lập",
      }).success,
    ).toBe(true);
  });

  it("rejects an invalid phone number", () => {
    const result = addressValuesSchema.safeParse({
      recipientName: "Nguyễn Văn A",
      phoneNumber: "invalid",
      province: "Hà Nội",
      district: "Ba Đình",
      ward: "Điện Biên",
      streetAddress: "12 Đường Độc Lập",
    });
    expect(result.success).toBe(false);
  });
});
