import { render, screen } from "@testing-library/react";
import { Card, CardTitle } from "@/components/ui/card";

describe("Card", () => {
  it("renders children", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<Card className="custom-class">Content</Card>);
    const card = screen.getByText("Content");
    expect(card.className).toContain("custom-class");
  });

  it("renders card title", () => {
    render(<CardTitle>My Title</CardTitle>);
    expect(screen.getByText("My Title")).toBeInTheDocument();
    expect(screen.getByText("My Title").tagName).toBe("H2");
  });
});
