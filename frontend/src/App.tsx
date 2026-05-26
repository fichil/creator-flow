import { useEffect, useState } from "react";

import { ProjectCreatePage } from "./pages/ProjectCreatePage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { ProjectListPage } from "./pages/ProjectListPage";

type Route =
  | { name: "list" }
  | { name: "create" }
  | { name: "detail"; projectId: number };

function parseRoute(): Route {
  const path = window.location.pathname;
  if (path === "/projects/new") {
    return { name: "create" };
  }
  const match = path.match(/^\/projects\/(\d+)$/);
  if (match) {
    return { name: "detail", projectId: Number(match[1]) };
  }
  return { name: "list" };
}

function navigate(path: string) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export default function App() {
  const [route, setRoute] = useState<Route>(() => parseRoute());

  useEffect(() => {
    const handler = () => setRoute(parseRoute());
    window.addEventListener("popstate", handler);
    return () => window.removeEventListener("popstate", handler);
  }, []);

  return (
    <main className="min-h-screen bg-stone-50 text-stone-950">
      {route.name === "list" && <ProjectListPage onCreate={() => navigate("/projects/new")} onOpen={(projectId) => navigate(`/projects/${projectId}`)} />}
      {route.name === "create" && <ProjectCreatePage onCancel={() => navigate("/")} onCreated={(projectId) => navigate(`/projects/${projectId}`)} />}
      {route.name === "detail" && <ProjectDetailPage projectId={route.projectId} onBack={() => navigate("/")} />}
    </main>
  );
}
