import { AxiosError } from "axios";
import { parseApiError } from "@/lib/api-error";

describe("parseApiError", () => {
  it("returns a network error message when no response exists", () => {
    const err = new AxiosError("Network Error", undefined, undefined, undefined, undefined);
    const result = parseApiError(err);
    expect(result.message).toContain("Network error");
    expect(result.technical).toContain("Network error");
  });

  it("returns a timeout message for ECONNABORTED", () => {
    const err = new AxiosError("timeout of 5000ms exceeded", "ECONNABORTED");
    const result = parseApiError(err);
    expect(result.message).toContain("timed out");
  });

  it("extracts backend detail from a 400 response", () => {
    const err = new AxiosError("Request failed with status code 400", undefined, undefined, undefined, {
      status: 400,
      data: { detail: "Email already registered" },
    } as any);
    const result = parseApiError(err);
    expect(result.message).toBe("Email already registered");
    expect(result.status).toBe(400);
  });

  it("returns a server error message for 500 responses", () => {
    const err = new AxiosError("Request failed with status code 500", undefined, undefined, undefined, {
      status: 500,
      data: {},
    } as any);
    const result = parseApiError(err);
    expect(result.message).toContain("Something went wrong");
    expect(result.status).toBe(500);
  });

  it("strips query strings and hashes from the request URL", () => {
    const err = new AxiosError("Network Error", undefined, { url: "/api/v1/auth/login?token=secret#hash" } as any);
    const result = parseApiError(err);
    expect(result.technical).toContain("/api/v1/auth/login");
    expect(result.technical).not.toContain("token=secret");
    expect(result.technical).not.toContain("#hash");
  });

  it("handles plain string errors", () => {
    const result = parseApiError("Something broke");
    expect(result.message).toBe("Something broke");
  });

  it("handles generic Error objects", () => {
    const result = parseApiError(new Error("Generic failure"));
    expect(result.message).toBe("Generic failure");
  });
});
