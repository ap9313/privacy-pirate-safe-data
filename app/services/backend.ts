const BACKEND_BASE = "http://localhost:8000";
const STATUS_ENDPOINT = `${BACKEND_BASE}/status`;
const FACE_BLUR_ENDPOINT = `${BACKEND_BASE}/process/image/blur`;
const DOCUMENT_BLUR_ENDPOINT = `${BACKEND_BASE}/process/document/blur`;
const TEXT_PROCESS_ENDPOINT = `${BACKEND_BASE}/process/text`;
const FORM_PROCESS_ENDPOINT = `${BACKEND_BASE}/process/form`;

export async function fetchBackendStatus() {
  const response = await fetch(STATUS_ENDPOINT);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

async function handleJsonResponse(response: Response, fallbackMessage: string) {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `${fallbackMessage} (${response.status})`);
  }
  return response.json();
}

export async function blurImage(file: File) {
  const formData = new FormData();
  formData.append("file", file, file.name);

  const response = await fetch(FACE_BLUR_ENDPOINT, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Blur request failed (${response.status})`);
  }

  const metadataHeader = response.headers.get("X-Privacy-Metadata");
  let metadata: Record<string, unknown> | null = null;
  if (metadataHeader) {
    try {
      metadata = JSON.parse(metadataHeader);
    } catch (error) {
      console.warn("Failed to parse image metadata header", error);
      metadata = null;
    }
  }
  const blob = await response.blob();
  const contentDisposition = response.headers.get("content-disposition");
  const filenameMatch = contentDisposition?.match(/filename="?([^";]+)"?/i);

  return {
    blob,
    filename: filenameMatch?.[1] ?? `blurred-${file.name}`,
    metadata,
  };
}

export async function blurDocument(file: File | Blob, epsilon = 1.0) {
  const formData = new FormData();
  const filename = file instanceof File && file.name ? file.name : "document.pdf";
  formData.append("file", file, filename);
  formData.append("epsilon", String(epsilon));

  const response = await fetch(DOCUMENT_BLUR_ENDPOINT, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Document blur request failed (${response.status})`);
  }

  const metadataHeader = response.headers.get("X-Document-Metadata") ?? response.headers.get("X-Metadata");
  let metadata: Record<string, unknown> | null = null;
  if (metadataHeader) {
    try {
      metadata = JSON.parse(metadataHeader);
    } catch (error) {
      console.warn("Failed to parse document metadata header", error);
      metadata = null;
    }
  }

  const blob = await response.blob();
  const contentDisposition = response.headers.get("content-disposition");
  const filenameMatch = contentDisposition?.match(/filename="?([^";]+)"?/i);

  return {
    blob,
    filename: filenameMatch?.[1] ?? `blurred-${filename}`,
    metadata,
  };
}

export async function processTextPayload(text: string, epsilon = 1.0) {
  const response = await fetch(TEXT_PROCESS_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, epsilon }),
  });

  return handleJsonResponse(response, "Text process request failed");
}

export async function processFormPayload(data: Record<string, unknown>, epsilon = 1.0) {
  const response = await fetch(FORM_PROCESS_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ data, epsilon }),
  });

  return handleJsonResponse(response, "Form process request failed");
}

export { STATUS_ENDPOINT, FACE_BLUR_ENDPOINT, DOCUMENT_BLUR_ENDPOINT };
