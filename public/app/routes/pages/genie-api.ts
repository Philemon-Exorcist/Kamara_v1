import { getBaseUrl } from "../api-config";
import { getAuthHeaders, getSessionUserKey } from "../auth/session";
import { SubscriptionRequiredError } from "../subscription-api";

export const GENERATED_COURSE_STORAGE_KEY = "kamara-generated-course";

export function getGeneratedCourseStorageKey() {
  return `${GENERATED_COURSE_STORAGE_KEY}:${getSessionUserKey()}`;
}

async function parseApiError(response: Response, fallback: string) {
  const errorData = await response.json().catch(() => ({}));

  if (typeof errorData?.error_code === "string" && errorData.error_code === "subscription_required") {
    throw new SubscriptionRequiredError(
      typeof errorData.message === "string" ? errorData.message : "Upgrade required.",
      errorData
    );
  }

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
    const error = await parseApiError(response, "Could not generate this course request.");
    if (error instanceof Error) {
      throw error;
    }
    throw new Error(error);
  }

  return readCourseGenerationStream(response);
}
