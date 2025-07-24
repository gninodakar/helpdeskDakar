<template>
  <Dialog v-model="open" :options="{ title: 'Create New Contact' }">
    <template #body-content>
      <div class="space-y-4">
        <!-- Two Columns -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
          <!-- Left Column -->
          <div
            v-for="field in leftFields"
            :key="field.label"
            class="flex flex-col gap-1"
          >
            <span class="mb-2 block text-sm leading-4 text-gray-700">
              {{ field.label }}
              <span v-if="field.required" class="text-red-500">*</span>
            </span>

            <!-- Dynamic Field Component -->
            <component
              :is="getComponent(field.type)"
              v-model="state[field.value]"
              v-bind="getComponentProps(field.type, field.value, field.placeholder)"
              @update:model-value="field.type === 'autocomplete' ? handleCustomerChange : null"
              @blur="field.action && field.action()"
            />

            <ErrorMessage :message="error[field.error]" />
          </div>

          <!-- Right Column -->
          <div
            v-for="field in rightFields"
            :key="field.label"
            class="flex flex-col gap-1"
          >
            <span class="mb-2 block text-sm leading-4 text-gray-700">
              {{ field.label }}
              <span v-if="field.required" class="text-red-500">*</span>
            </span>

            <!-- Dynamic Field Component -->
            <component
              :is="getComponent(field.type)"
              v-model="state[field.value]"
              v-bind="getComponentProps(field.type, field.value, field.placeholder)"
              @update:model-value="field.type === 'autocomplete' ? handleCustomerChange : null"
              @blur="field.action && field.action()"
            />

            <ErrorMessage :message="error[field.error]" />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-2">
          <Button
            label="Create"
            :loading="contactResource.loading"
            theme="gray"
            variant="solid"
            @click="createContact()"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>



<script setup lang="ts">
import { computed, ref } from "vue";
import {
  Autocomplete,
  Dialog,
  ErrorMessage,
  Input,
  createListResource,
  createResource,
  toast,
} from "frappe-ui";
import zod from "zod";
import { AutoCompleteItem } from "@/types";
import { useContactStore } from "@/stores/contact";

interface Props {
  modelValue: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (event: "update:modelValue", value: boolean): void;
  (event: "close"): void;
  (event: "contactCreated"): void;
}>();

const contactStore = useContactStore();

const state = ref({
  emailID: "",
  firstName: "",
  lastName: "",
  phone: "",
  selectedCustomer: "",
  designation: "",
});

const error = ref({
  emailValidationError: "",
  firstNameValidationError: "",
  lastNameValidationError: "",
  phoneValidationError: "",
  customerValidationError: "",
  designationValidationError: "",
});

const open = computed({
  get: () => props.modelValue,
  set: (val) => {
    emit("update:modelValue", val);
    if (!val) emit("close");
  },
});

const customerResource = createListResource({
  doctype: "HD Customer",
  fields: ["name"],
  cache: "customers",
  auto: true,
  searchField: "name", 
  transform: (data) =>
    Array.isArray(data)
      ? data.map((option) => ({
          label: option.name,  
          value: option.name,  
        }))
      : [],
});


const contactResource = createResource({
  url: "frappe.client.insert",
  onSuccess: () => {
    resetForm();
    toast.success("Contact created");
    emit("contactCreated");
  },
});

function createContact() {
  if (validateInputs()) return;

  const doc: any = {
    doctype: "Contact",
    first_name: state.value.firstName,
    last_name: state.value.lastName,
    email_ids: [{ email_id: state.value.emailID, is_primary: true }],
    links: [],
    phone_nos: [],
    designation: state.value.designation,
    company_name: state.value.selectedCustomer,
  };

  if (state.value.phone) {
    doc.phone_nos.push({ phone: state.value.phone });
  }
  if (state.value.selectedCustomer) {
    doc.links.push({
      link_doctype: "HD Customer",
      link_name: state.value.selectedCustomer,
    });
  }

  contactResource.submit({ doc });
}

function handleCustomerChange(item: AutoCompleteItem | null) {
  state.value.selectedCustomer = item?.value || "";
}

function validateInputs() {
  return [
    validateEmailInput(state.value.emailID),
    validateFirstName(state.value.firstName),
    validatePhone(state.value.phone),
  ].some(Boolean);
}

function validateEmailInput(value: string) {
  error.value.emailValidationError = "";
  const success = zod.string().email().safeParse(value).success;

  if (!value) {
    error.value.emailValidationError = "Email should not be empty";
  } else if (!success) {
    error.value.emailValidationError = "Enter a valid email";
  } else if (existingContactEmails(contactStore.options).includes(value)) {
    error.value.emailValidationError = "Contact with email already exists";
  }
  return error.value.emailValidationError;
}

function validateFirstName(value: string) {
  error.value.firstNameValidationError = "";
  if (!value?.trim()) {
    error.value.firstNameValidationError = "First name should not be empty";
  }
  return error.value.firstNameValidationError;
}

function validatePhone(value: string) {
  error.value.phoneValidationError = "";
  const reg = /[0-9]+/;
  if (value && (!reg.test(value) || value.length < 8)) {
    error.value.phoneValidationError = "Enter a valid phone number";
  }
  return error.value.phoneValidationError;
}

function existingContactEmails(contacts) {
  return contacts.map((c) => c.email_id);
}

function resetForm() {
  state.value = {
    emailID: "",
    firstName: "",
    lastName: "",
    phone: "",
    selectedCustomer: "",
    designation: "",
  };
}

// Field config
const formFields = [
  { label: "Email Id", value: "emailID", error: "emailValidationError", type: "input", required: true, placeholder: "Enter your email", action: () => validateEmailInput(state.value.emailID) },
  { label: "First Name", value: "firstName", error: "firstNameValidationError", type: "input", required: true, placeholder: "First Name", action: () => validateFirstName(state.value.firstName) },
  { label: "Last Name", value: "lastName", error: "lastNameValidationError", type: "input", required: false, placeholder: "Last Name" },
  { label: "Designation", value: "designation", error: "designationValidationError", type: "input", required: false, placeholder: "Designation" },
  { label: "Phone", value: "phone", error: "phoneValidationError", type: "input", required: false, placeholder: "Phone Number", action: () => validatePhone(state.value.phone) },
  { label: "Customer", value: "selectedCustomer", error: "customerValidationError", type: "autocomplete", required: false, placeholder: "Customer" },
];


const mid = Math.ceil(formFields.length / 2);
const leftFields = formFields.slice(0, mid);
const rightFields = formFields.slice(mid);

// Dynamic component mapping
function getComponent(type: string) {
  if (type === "autocomplete") return Autocomplete;
  return Input;
}

function getComponentProps(type: string, value: string, placeholder?: string) {
  if (type === "autocomplete") {
    return {
      placeholder,
      options: customerResource.data || [],
    };
  }
  return {
    name: value,
    placeholder,
    type: "text",
  };
}
</script>

<style></style>
