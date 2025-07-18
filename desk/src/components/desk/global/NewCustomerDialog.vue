<template>
  <div>
    <Dialog
      v-model="model"
      :options="{ title: 'Add New Customer', size: 'md' }" >
      <template #body-content>
        <div class="space-y-4">
          <div class="flex gap-4"> <div class="flex-1 space-y-1"> <Input
                v-model="state.customer"
                label="Customer Name"
                type="text"
                placeholder="Your company name."
              />
              <Input
                v-model="state.address"
                label="Address"
                type="text"
                placeholder="Address"
              />
              <Input
                v-model="state.vat"
                label="VAT"
                type="text"
                placeholder="VAT"
              />
              <Input
                v-model="state.reg_num"
                label="Registration Number"
                type="text"
                placeholder="Registration Number"
              />
              <Input
                v-model="state.email"
                label="Email"
                type="text"
                placeholder="Email"
              />
            </div>

            <div class="flex-1 space-y-1">
              <Input
                v-model="state.phone"
                label="Phone Number"
                type="text"
                placeholder="Phone Number"
              />
              <Input
                v-model="state.hosting_status"
                label="Hosting Status"
                type="text"
                placeholder="Hosting Status"
              />
              <Input
                v-model="state.engagement_date"
                label="Engagement Date"
                type="text"
                placeholder="Engagement Date"
              />
              <Input
                v-model="state.type_of_client"
                label="Type of Client"
                type="text"
                placeholder="Type of Client"
              />
              <Input
                v-model="state.domain"
                label="Domain"
                type="text"
                placeholder="e.g.:mycompany.com"
              />
            </div>
          </div>

          <div class="float-right flex space-x-2">
            <Button
              label="Add"
              theme="gray"
              variant="solid"
              @click.prevent="addCustomer"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { Dialog, Input, createResource, toast } from "frappe-ui";
import { reactive } from "vue";
// import { custom } from "zod"; // 'custom' is not used here, consider removing if not needed

const emit = defineEmits(["customerCreated"]);
const model = defineModel<boolean>();

const state = reactive({
  customer: "",
  address: "",
  vat: "",
  reg_num: "",
  email: "",
  phone: "",
  hosting_status: "",
  engagement_date: "",
  type_of_client: "",
  domain: "",
});

const customerResource = createResource({
  url: "frappe.client.insert",
  method: "POST",
  data: {
    doc: {
      doctype: "HD Customer",
      customer_name: state.customer,
      customer_address: state.address,
      vat: state.vat, // Asegúrate de que los nombres de los campos aquí coincidan con los de tu DocType 'HD Customer'
      reg_num: state.reg_num,
      email: state.email,
      phone: state.phone,
      hosting_status: state.hosting_status,
      engagement_date: state.engagement_date,
      type_of_client: state.type_of_client,
      domain: state.domain,
    },
  },
  onSuccess: () => {
    // Limpia los campos después de la creación exitosa
    state.customer = "";
    state.address = "";
    state.vat = "";
    state.reg_num = "";
    state.email = "";
    state.phone = "";
    state.hosting_status = "";
    state.engagement_date = "";
    state.type_of_client = "";
    state.domain = "";
    toast.success("Customer created");
    emit("customerCreated");
  },
  onError: (err) => {
    toast.error(err.messages[0]);
  },
});

function addCustomer() {
  if (!state.customer) {
    toast.error("Customer name is required");
    return;
  }
  customerResource.submit({
    doc: {
      doctype: "HD Customer",
      customer_name: state.customer,
      customer_address: state.address,
      customer_vat: state.vat, // Asegúrate de que estos nombres de campo estén correctos para tu DocType
      customer_reg_num: state.reg_num,
      customer_email: state.email,
      customer_phone: state.phone,
      customer_hosting_status: state.hosting_status,
      customer_engagement_date: state.engagement_date,
      customer_type_of_client: state.type_of_client,
      customer_domain: state.domain,
    },
  });
}
</script>