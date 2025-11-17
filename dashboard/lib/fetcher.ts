export class FetchError<T> extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: T
  ) {
    super(`Fetch Error: ${status} ${statusText}`);
    this.name = "FetchError";
  }
}

const request = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const data = await response
        .json()
        .catch(() => ({ message: "Invalid response format" }));

      throw new FetchError(response.status, response.statusText, data);
    }

    return response;
  } catch (error) {
    if (error instanceof FetchError) {
      throw error;
    }

    const message =
      error instanceof Error ? error.message : "An unknown error occurred";

    throw new FetchError(500, "Unknown error occurred", { message });
  }
};

export const fetcher = {
  get: (endpoint: string, options: RequestInit = {}) =>
    request(endpoint, { ...options, method: "GET" }),

  post: (endpoint: string, data?: unknown, options: RequestInit = {}) =>
    request(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: (endpoint: string, data?: unknown, options: RequestInit = {}) =>
    request(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: (endpoint: string, options: RequestInit = {}) =>
    request(endpoint, { ...options, method: "DELETE" }),
};
