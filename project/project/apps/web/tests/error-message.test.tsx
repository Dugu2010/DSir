import { render, screen } from "@testing-library/react";
import { ErrorMessage } from "@/components/ui/error-message";

describe("ErrorMessage", () => {
  it("renders children", () => {
    render(<ErrorMessage>Something went wrong</ErrorMessage>);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<ErrorMessage className="mb-4">Error</ErrorMessage>);
    const error = screen.getByText("Error");
    expect(error.className).toContain("mb-4");
  });
});
