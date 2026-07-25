import { getAuthHeaders, getSessionUserKey } from "../auth/session";

const LOCAL_API_URL = "http://localhost:8001/api/v1";
// const PRODUCTION_API_URL = "https://kamsi-xza9.onrender.com/api/v1";
const PRODUCTION_API_URL = "https://kamsi-t57w.onrender.com/api/v1";

export const GENERATED_COURSE_STORAGE_KEY = "kamara-generated-course";

export function getGeneratedCourseStorageKey() {
  return `${GENERATED_COURSE_STORAGE_KEY}:${getSessionUserKey()}`;
}

function getBaseUrl() {
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    return LOCAL_API_URL;
  }

  return PRODUCTION_API_URL;
}

async function parseApiError(response: Response, fallback: string) {
  const errorData = await response.json().catch(() => ({}));

  if (typeof errorData.detail === "string") {
    return errorData.detail;
  }

  if (Array.isArray(errorData.detail)) {
    return errorData.detail
      .map((error: any) => error.msg)
      .filter(Boolean)
      .join(" ");
  }

  return fallback;
}

async function readCourseGenerationStream(response: Response) {
  if (!response.body) {
    return response.json();
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let latestPayload: any = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const dataLine = event
        .split("\n")
        .find((line) => line.startsWith("data:"));

      if (!dataLine) {
        continue;
      }

      const payload = JSON.parse(dataLine.replace(/^data:\s*/, ""));
      latestPayload = payload;

      if (payload.status === "error") {
        throw new Error(payload.message || "Could not generate this course request.");
      }

      if (payload.status === "complete") {
        return payload;
      }
    }
  }

  return latestPayload ?? { status: "complete" };
}

export async function submitCoursePrompt({
  courseTitle,
  prompt,
}: {
  courseTitle: string;
  courseDescription: string;
  prompt: string;
  photos: File[];
}) {
  let response: Response;

  const requestInit: RequestInit = {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      course: courseTitle,
      prompt,
    }),
  };

  try {
    response = await fetch(`${getBaseUrl()}/pages/course/generate`, requestInit);

    if (response.status === 404) {
      response = await fetch(`${getBaseUrl()}/courses/generate`, requestInit);
    }
  } catch {
    throw new Error("Could not reach the backend. Please check your connection and try again.");
  }

  if (!response.ok) {
    throw new Error(await parseApiError(response, "Could not generate this course request."));
  }

  return readCourseGenerationStream(response);
}
