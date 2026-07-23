import { useAuthStore } from "@/hooks/use-auth";

describe("useAuthStore", () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false });
  });

  it("starts unauthenticated", () => {
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().user).toBeNull();
  });

  it("logs in a user", () => {
    const user = {
      id: "1",
      email: "test@example.com",
      full_name: "Test User",
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
    };
    useAuthStore.getState().login(user);
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().user).toEqual(user);
  });

  it("logs out a user", () => {
    useAuthStore.getState().login({
      id: "1",
      email: "test@example.com",
      full_name: "Test User",
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
    });
    useAuthStore.getState().logout();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().user).toBeNull();
  });
});
