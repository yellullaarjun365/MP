const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail = "Request failed.";

    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
    }

    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}
