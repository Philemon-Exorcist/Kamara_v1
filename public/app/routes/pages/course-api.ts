import { getAuthHeaders, getSessionUserKey } from "../auth/session";

const LOCAL_API_URL = "http://localhost:8001/api/v1";
const PRODUCTION_API_URL = "https://kamsi-t57w.onrender.com/api/v1"; // This could be an environment variable

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
      .filter(Boolean) // Filter out any empty messages
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

interface CoursePromptPayload {
  courseTitle: string;
  prompt: string;
}

export async function submitCoursePrompt({
  courseTitle,
  prompt,
}: CoursePromptPayload) {
  let response: Response;

  // The endpoint path seems to have two variants, let's try the primary one first.
  const primaryPath = "/pages/course/generate";
  const requestBody = {
    course: courseTitle,
    prompt,
  };

  const requestInit: RequestInit = {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  };

  try {
    response = await fetch(`${getBaseUrl()}${primaryPath}`, requestInit);

    // If the primary endpoint is not found, try the fallback endpoint.
    if (response.status === 404) {
      const fallbackPath = "/courses/generate";
      console.warn(`Endpoint ${primaryPath} not found, trying fallback ${fallbackPath}`);
      response = await fetch(`${getBaseUrl()}/courses/generate`, requestInit);
    }
  } catch (error) {
    console.error("Network error during course generation:", error);
    throw new Error("Could not reach the backend. Please check your connection and try again.");
  }

  // After attempting fetches, check if the final response is OK.
  if (!response.ok) {
    throw new Error(await parseApiError(response, "Could not generate this course request."));
  }

  return readCourseGenerationStream(response);
}
