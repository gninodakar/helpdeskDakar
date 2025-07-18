<template>
  <Dialog :options="options">
    <template #body-main>
      <div class="flex flex-col items-center gap-4 p-6">
        <!-- Customer name & avatar -->
        <div class="text-xl font-medium text-gray-900">
          {{ customer.doc?.name }}
        </div>
        <Avatar
          size="lg"
          :label="customer.doc?.name"
          :image="customer.doc?.image"
          class="cursor-pointer hover:opacity-80"
        />

        <!-- Upload / remove photo -->
        <div class="flex gap-2">
          <FileUploader @success="(file) => updateImage(file)">
            <template #default="{ uploading, openFileSelector }">
              <Button
                :label="customer.doc?.image ? 'Change photo' : 'Upload photo'"
                :loading="uploading"
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <Button
            v-if="customer.doc?.image"
            label="Remove photo"
            @click="updateImage(null)"
          />
        </div>

        <!-- Two-column form -->
        <form class="w-full" @submit.prevent="update">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
            <Input
              v-for="field in fields"
              :key="field.key"
              v-model="field.model"
              :label="field.label"
              :placeholder="field.label"
            />
          </div>
        </form>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import {
  Avatar,
  createDocumentResource,
  Dialog,
  FileUploader,
  toast,
} from "frappe-ui";
import { computed } from "vue";

const props = defineProps({ name: String });
const emit = defineEmits(["customer-updated"]);

const customer = createDocumentResource({
  doctype: "HD Customer",
  name: props.name,
  fields: [
    "name", "image", "customer_name", "address", "vat", "registration_number",
    "email", "phone_number", "hosting_status", "engagement_date",
    "type_of_client", "domain",
  ],
  auto: true,
  setValue: {
    onSuccess: () => toast.success("Customer updated"),
    onError: () => toast.error("Error updating customer"),
  },
});

// Helper for computeds
function createField(key: string) {
  return computed({
    get: () => customer.doc?.[key],
    set: (v) => customer.setValue.submit({ [key]: v }),
  });
}

// forms fields
const fields = [
  { key: "customer_name", label: "Customer Name" },
  { key: "address", label: "Address" },
  { key: "vat", label: "VAT" },
  { key: "registration_number", label: "Registration Number" },
  { key: "email", label: "Email" },
  { key: "phone_number", label: "Phone Number" },
  { key: "hosting_status", label: "Hosting Status" },
  { key: "engagement_date", label: "Engagement Date" },
  { key: "type_of_client", label: "Type of Client" },
  { key: "domain", label: "Domain" },
].map(f => ({ ...f, model: createField(f.key) }));

// dialog btns
const options = computed(() => ({
  title: customer.doc?.name,
  actions: [
    {
      label: "Save",
      theme: "gray",
      variant: "solid",
      onClick: update,
    },
  ],
}));

// save changes
async function update() {
  const data = Object.fromEntries(fields.map(f => [f.key, f.model.value]));
  await customer.setValue.submit(data);
  emit("customer-updated");
}

// update image
function updateImage(file) {
  customer.setValue.submit({ image: file?.file_url || null });
  emit("customer-updated");
}
</script>
