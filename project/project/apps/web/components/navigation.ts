import {
  FolderCode,
  LayoutDashboard,
  Library,
  Map,
  RotateCcw,
  Settings,
  User,
} from "lucide-react";

export const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Courses", href: "/courses", icon: Library },
  { name: "Roadmaps", href: "/roadmaps", icon: Map },
  { name: "Revision", href: "/revision", icon: RotateCcw },
  { name: "Projects", href: "/projects", icon: FolderCode },
  { name: "Profile", href: "/profile", icon: User },
  { name: "Settings", href: "/settings", icon: Settings },
];
