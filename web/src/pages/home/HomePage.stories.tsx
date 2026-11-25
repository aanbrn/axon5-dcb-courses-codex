import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, waitFor } from "storybook/test";
import { HomePage } from "./HomePage";

const roleKey = "courses.demo.role";
const administrator = {
  id: "29807e59-c312-49d1-9654-e3c995ed066f",
  label: "Administrator",
  kind: "administrator",
};
const maya = { id: "3dd449cf-25d6-4b78-bb71-90e7f46419c2", label: "Maya Chen", kind: "student" };
const alex = { id: "f6dfcd57-f874-48ee-b85b-1f0965e7f09a", label: "Alex Rivera", kind: "student" };
const longName = {
  ...alex,
  label: "Alex Rivera — Graduate Student in Distributed Systems and Event-Driven Architecture",
};
const missingStudentId = "76acfe35-a911-4bf8-a46e-8d87e809083a";
const loadingMessage = "Loading demo roles…";
const errorMessage = "Could not load demo roles. Try again to switch roles.";
const fallbackMessage = "Your previous demo student is unavailable. You’re now using Administrator.";

const directory = (...students: (typeof maya)[]) => () => Response.json({ administrator, students });
const unavailable = () => new Response(null, { status: 503 });
const continueLoading = () => new Promise<Response>(() => {});

function mockDirectory(
  responses: (() => Response | Promise<Response>)[],
  savedId?: string,
  onRequest?: () => void,
) {
  return () => {
    const originalFetch = window.fetch;
    const previousRole = sessionStorage.getItem(roleKey);
    let attempts = 0;
    if (savedId === undefined) sessionStorage.removeItem(roleKey);
    else sessionStorage.setItem(roleKey, savedId);

    window.fetch = async (input, init) => {
      const url = new URL(input instanceof Request ? input.url : input, window.location.href);
      if (url.origin !== window.location.origin || url.pathname !== "/api/demo-roles") {
        return originalFetch(input, init);
      }
      onRequest?.();
      const respond = responses[attempts++];
      if (!respond) throw new Error("Unexpected demo-role request");
      return respond();
    };

    return () => {
      window.fetch = originalFetch;
      if (previousRole === null) sessionStorage.removeItem(roleKey);
      else sessionStorage.setItem(roleKey, previousRole);
    };
  };
}

const meta = {
  title: "Shell/Home",
  component: HomePage,
  args: { docsBase: new URL("http://127.0.0.1:8081/") },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof HomePage>;

export default meta;
type Story = StoryObj<typeof meta>;
type Interaction = Parameters<NonNullable<Story["play"]>>[0];

async function expectFailure({ canvas }: Interaction) {
  await expect(await canvas.findByRole("alert")).toHaveTextContent(errorMessage);
  await expect(canvas.getByRole("combobox", { name: "Demo role" })).toBeDisabled();
  await expect(canvas.getByRole("option", { name: "Roles unavailable" })).toHaveProperty("selected", true);
  await expect(canvas.getByRole("link", { name: "Documentation" })).toBeVisible();
}

export const Populated: Story = {
  beforeEach: mockDirectory([directory(maya, alex)]),
  play: async ({ canvas, userEvent }) => {
    const select = canvas.getByRole("combobox", { name: "Demo role" });
    await canvas.findByRole("option", { name: alex.label });
    await expect(canvas.getAllByRole("option").map((option) => option.textContent)).toEqual([
      administrator.label,
      maya.label,
      alex.label,
    ]);
    await expect(select).toHaveValue(administrator.id);

    const skip = canvas.getByRole("link", { name: "Skip to main content" });
    await userEvent.tab();
    await expect(skip).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("link", { name: "DCB Courses" })).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("link", { name: "Documentation" })).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("link", { name: /^Quick start$/ })).toHaveFocus();
    await userEvent.tab();
    await expect(select).toHaveFocus();
    await userEvent.tab({ shift: true });
    await expect(canvas.getByRole("link", { name: /^Quick start$/ })).toHaveFocus();
    await userEvent.tab();
    await expect(select).toHaveFocus();
    await userEvent.selectOptions(select, maya.id);
    await expect(select).toHaveValue(maya.id);
    await expect(select).toHaveFocus();
    await expect(sessionStorage.getItem(roleKey)).toBe(maya.id);
  },
};

export const Loading: Story = {
  beforeEach: mockDirectory([continueLoading]),
  play: async ({ canvas }) => {
    const select = canvas.getByRole("combobox", { name: "Demo role" });
    await expect(select).toBeDisabled();
    await expect(await canvas.findByRole("option", { name: loadingMessage })).toHaveProperty("selected", true);
    await waitFor(() => expect(canvas.getByRole("status")).toHaveTextContent(loadingMessage));
    await expect(canvas.getByRole("link", { name: "Documentation" })).toBeVisible();
  },
};

export const AdministratorOnly: Story = {
  beforeEach: mockDirectory([directory()]),
  play: async ({ canvas }) => {
    await expect(await canvas.findByRole("heading", { name: "No demo students available" })).toBeVisible();
    await expect(canvas.getByRole("combobox", { name: "Demo role" })).toHaveValue(administrator.id);
    await expect(canvas.getAllByRole("link", { name: /^quick start$/i })).toHaveLength(2);
  },
};

export const MissingSavedStudent: Story = {
  beforeEach: mockDirectory([directory()], missingStudentId),
  play: async ({ canvas }) => {
    const status = canvas.getByRole("status");
    await waitFor(() => expect(status).toHaveTextContent(fallbackMessage));
    await expect(canvas.getByRole("status")).toBe(status);
    await expect(canvas.getByRole("combobox", { name: "Demo role" })).toHaveValue(administrator.id);
    await expect(canvas.getByRole("heading", { name: "No demo students available" })).toBeVisible();
    await expect(sessionStorage.getItem(roleKey)).toBe(administrator.id);
  },
};

export const InitialError: Story = {
  beforeEach: mockDirectory([unavailable], maya.id),
  play: async (context) => {
    await expectFailure(context);
    await expect(context.canvas.getByRole("button", { name: "Retry loading roles" })).toBeEnabled();
    await expect(sessionStorage.getItem(roleKey)).toBe(maya.id);
  },
};

function retryStory(key: "{Enter}" | " ", result?: () => Response): Story {
  let finishRetry: (response: Response) => void;
  let requests: number;
  return {
    beforeEach: () => {
      requests = 0;
      return mockDirectory([
        unavailable,
        () => new Promise<Response>((resolve) => { finishRetry = resolve; }),
      ], maya.id, () => { requests++; })();
    },
    play: async (context) => {
      const { canvas, userEvent } = context;
      await expectFailure(context);
      const status = canvas.getByRole("status");
      const button = canvas.getByRole("button", { name: "Retry loading roles" });

      canvas.getByRole("link", { name: /^Quick start$/ }).focus();
      await userEvent.tab();
      await expect(button).toHaveFocus();
      await userEvent.keyboard(key);
      await waitFor(() => expect(button).toHaveAttribute("aria-disabled", "true"));
      await expect(button).toHaveFocus();
      await expect(canvas.getByRole("status")).toBe(status);
      await expect(status).toHaveTextContent(loadingMessage);
      await userEvent.keyboard("{Enter} ");
      await expect(requests).toBe(2);
      await expect(sessionStorage.getItem(roleKey)).toBe(maya.id);
      if (!result) return;

      finishRetry(result());
      if (result === unavailable) {
        await expectFailure(context);
        await expect(canvas.getByRole("button", { name: "Retry loading roles" })).toBe(button);
        await expect(button).toHaveAttribute("aria-disabled", "false");
        await expect(button).toHaveFocus();
      } else {
        await canvas.findByRole("option", { name: maya.label });
        const select = canvas.getByRole("combobox", { name: "Demo role" });
        await expect(select).toHaveValue(maya.id);
        await expect(select).toHaveFocus();
        await expect(canvas.queryByRole("button", { name: "Retry loading roles" })).toBeNull();
      }
      await expect(canvas.getByRole("status")).toBe(status);
      await expect(status).toBeEmptyDOMElement();
    },
  };
}

export const RetryPending: Story = retryStory("{Enter}");
export const RetrySuccess: Story = retryStory(" ", directory(maya));
export const RetryFailure: Story = retryStory("{Enter}", unavailable);

export const NarrowWithLongName: Story = {
  beforeEach: mockDirectory([directory(longName)], longName.id),
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas }) => {
    await expect(await canvas.findByRole("option", { name: longName.label })).toHaveProperty("selected", true);
    await expect(await canvas.findByText(longName.label, { selector: "p" })).toBeVisible();
  },
};

export const MalformedResponse: Story = {
  beforeEach: mockDirectory([
    () => new Response('{"administrator":', { headers: { "Content-Type": "application/json" } }),
  ], maya.id),
  play: async (context) => {
    await expectFailure(context);
    await expect(sessionStorage.getItem(roleKey)).toBe(maya.id);
  },
};
