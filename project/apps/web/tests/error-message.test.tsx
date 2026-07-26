import { render, screen } from "@testing-library/react";
import { ErrorMessage } from "@/components/ui/error-message";

describe("ErrorMessage", () => {
  it("renders children", () => {
    render(<ErrorMessage>Something went wrong</ErrorMessage>);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(<ErrorMessage className="mb-4">Error</ErrorMessage>);
    expect(container.firstChild).toHaveClass("mb-4");
  });

  it("renders technical details when provided", () => {
    render(<ErrorMessage details="GET /api/v1/auth/me failed with status 500">Network error</ErrorMessage>);
    expect(screen.getByText("Network error")).toBeInTheDocument();
    expect(screen.getByText("Technical details")).toBeInTheDocument();
    expect(screen.getByText("GET /api/v1/auth/me failed with status 500")).toBeInTheDocument();
  });

  it("does not render details when not provided", () => {
    render(<ErrorMessage>Simple error</ErrorMessage>);
    expect(screen.getByText("Simple error")).toBeInTheDocument();
    expect(screen.queryByText("Technical details")).not.toBeInTheDocument();
  });
});
