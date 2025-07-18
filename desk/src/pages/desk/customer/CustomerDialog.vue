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
            <!-- Column 1 -->
            <Input v-model="domain" label="Customer Name" placeholder="Customer Name" />
            <Input v-model="domain" label="Address" placeholder="Address" />
            <Input v-model="domain" label="VAT" placeholder="VAT" />
            <Input v-model="domain" label="Registration Number" placeholder="Registration Number" />
            <Input v-model="domain" label="Email" placeholder="Email" />

            <!-- Column 2 -->
            <Input v-model="domain" label="Phone Number" placeholder="Phone Number" />
            <Input v-model="domain" label="Hosting Status" placeholder="Hosting Status" />
            <Input v-model="domain" label="Engagement Date" placeholder="Engagement Date" />
            <Input v-model="domain" label="Type of Client" placeholder="Type of Client" />
            <Input v-model="domain" label="Domain" placeholder="example.com" />
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

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["customer-updated"]);

const customer = createDocumentResource({
  doctype: "HD Customer",
  name: props.name,
  fields:[
    "name",
    "image",
    "customer_name",
    "address",
    "vat",
    "registration_number",
    "email",
    "phone_number",
    "hosting_status",
    "engagement_date",
    "type_of_client",
    "domain",
  ],
  auto: true,
  setValue: {
    onSuccess() {
      toast.success("Customer updated");
    },
    onError() {
      toast.error("Error updating customer");
    },
  },
});

//gettters and setters
const customerName = computed({
  get: () => customer.doc?.customer_name,
  set: (v) => customer.setValue.submit({ customer_name: v }),
});

const address = computed({
  get: () => customer.doc?.address,
  set: (v) => customer.setValue.submit({ address: v }),
});

const vat = computed({
  get: () => customer.doc?.vat,
  set: (v) => customer.setValue.submit({ vat: v }),
});

const registrationNumber = computed({
  get: () => customer.doc?.registration_number,
  set: (v) => customer.setValue.submit({ registration_number: v }),
});

const email = computed({
  get: () => customer.doc?.email,
  set: (v) => customer.setValue.submit({ email: v }),
});

const phoneNumber = computed({
  get: () => customer.doc?.phone_number,
  set: (v) => customer.setValue.submit({ phone_number: v }),
});

const hostingStatus = computed({
  get: () => customer.doc?.hosting_status,
  set: (v) => customer.setValue.submit({ hosting_status: v }),
});

const engagementDate = computed({
  get: () => customer.doc?.engagement_date,
  set: (v) => customer.setValue.submit({ engagement_date: v }),
});

const typeOfClient = computed({
  get: () => customer.doc?.type_of_client,
  set: (v) => customer.setValue.submit({ type_of_client: v }),
});

const domain = computed({
  get: () => customer.doc?.domain,
  set: (v) => customer.setValue.submit({ domain: v }),
});

const options = computed(() => ({
  title: customer.doc?.name,
  actions: [
    {
      label: "Save",
      theme: "gray",
      variant: "solid",
      onClick: () => update(),
    },
  ],
}));

async function update() {
  await customer.setValue.submit({
    customer_name: customerName.value,
    customer_address: address.value,
    customer_vat: vat.value,
    customer_reg_num: registrationNumber.value,
    customer_email: email.value,
    customer_phone: phoneNumber.value,
    customer_hosting_status: hostingStatus.value,
    customer_engagement_date: engagementDate.value,
    customer_type_of_client: typeOfClient.value,
    domain: domain.value,
  });
  emit("customer-updated");
}

/* image is still handled separately */
function updateImage(file) {
  customer.setValue.submit({ image: file?.file_url || null });
  emit("customer-updated");
}
</script>