import { AquaLifeShell } from "@/components/app-shell/app-shell";

export default function WorkspaceLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <AquaLifeShell>{children}</AquaLifeShell>;
}
