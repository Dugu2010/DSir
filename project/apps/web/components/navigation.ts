import {
  FileInput,
  FolderCode,
  LayoutDashboard,
  Library,
  Map,
  Mic,
  RotateCcw,
  Settings,
  Sparkles,
  User,
} from "lucide-react";

export const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Courses", href: "/courses", icon: Library },
  { name: "Import Course", href: "/import-course", icon: FileInput },
  { name: "Roadmaps", href: "/roadmaps", icon: Map },
  { name: "AI Roadmap", href: "/roadmaps/generate", icon: Sparkles },
  { name: "Interview", href: "/interview", icon: Mic },
  { name: "Revision", href: "/revision", icon: RotateCcw },
  { name: "Projects", href: "/projects", icon: FolderCode },
  { name: "Profile", href: "/profile", icon: User },
  { name: "Settings", href: "/settings", icon: Settings },
];
