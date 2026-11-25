import type { Meta, StoryObj } from "@storybook/react-vite";
import { CircleAlertIcon } from "lucide-react";
import { expect } from "storybook/test";
import { Alert, AlertDescription, Button, NativeSelect, NativeSelectOption } from "./index";

const meta = {
  title: "Shared/Controls",
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const RoleSelector: Story = {
  render: () => (
    <div className="role-group">
      <label htmlFor="story-demo-role">Demo role</label>
      <NativeSelect id="story-demo-role" defaultValue="administrator">
        <NativeSelectOption value="administrator">Administrator</NativeSelectOption>
        <NativeSelectOption value="maya">Maya Chen</NativeSelectOption>
        <NativeSelectOption value="alex">Alex Rivera</NativeSelectOption>
      </NativeSelect>
    </div>
  ),
  play: async ({ canvas, userEvent }) => {
    const select = canvas.getByRole("combobox", { name: "Demo role" });
    await userEvent.selectOptions(select, "maya");
    await expect(select).toHaveValue("maya");
  },
};

export const Actions: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-4">
      <Button asChild>
        <a href="http://127.0.0.1:8081/feasibility/phase-01/">Read feasibility report</a>
      </Button>
      <Button type="button" variant="outline">
        Retry loading roles
      </Button>
    </div>
  ),
};

export const DirectoryAlert: Story = {
  render: () => (
    <Alert variant="destructive">
      <CircleAlertIcon aria-hidden="true" />
      <AlertDescription>Could not load demo roles. Try again to switch roles.</AlertDescription>
    </Alert>
  ),
};
