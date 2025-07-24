<template>
  <div class="time-sheet-form p-4 border rounded-md bg-white shadow-sm">
    <h3 class="text-lg font-semibold mb-4">Add Time Sheet Entry</h3>
    <form @submit.prevent="addTimeSheetRow" class="space-y-4">
      <div>
        <label for="event" class="block text-sm font-medium text-gray-700">Event Type</label>
        <select
          id="event"
          v-model="form.eventType"
          class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          required
        >
          <option value="">Select an event</option>
          <option v-for="event in eventTypes" :key="event.value" :value="event.value">
            {{ event.label }}
          </option>
        </select>
      </div>

      <div>
        <label for="duration" class="block text-sm font-medium text-gray-700">Duration (hours)</label>
        <input
          type="number"
          id="duration"
          v-model.number="form.duration"
          class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
          min="0.1"
          step="0.1"
          required
        />
      </div>

      <div>
        <label for="date" class="block text-sm font-medium text-gray-700">Date</label>
        <input
          type="date"
          id="date"
          v-model="form.date"
          class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
          required
        />
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          id="description"
          v-model="form.description"
          rows="3"
          class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
        ></textarea>
      </div>

      <Button
        type="submit"
        label="Add Entry"
        variant="solid"
        :loading="isLoading"
        class="w-full justify-center"
      />
    </form>
    <div v-if="timeSheetEntries.length" class="mt-8">
      <h4 class="text-md font-semibold mb-3">Current Time Sheet Entries</h4>
      <ul class="divide-y divide-gray-200">
        <li v-for="(entry, index) in timeSheetEntries" :key="index" class="py-3 flex justify-between items-center">
          <div>
            <p class="text-sm font-medium text-gray-900">{{ entry.eventType }} - {{ entry.duration }} hours</p>
            <p class="text-xs text-gray-500">{{ entry.date }}</p>
            <p v-if="entry.description" class="text-sm text-gray-600">{{ entry.description }}</p>
          </div>
        <button
            type="button"
            @click="deleteTimeSheetEntry(index)"
            class="text-red-500 hover:text-red-700 px-2 py-1.5 rounded text-sm"
            >
            Delete
        </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { call, toast, createResource } from 'frappe-ui';
// import Button from '@/components/Button.vue'; // Adjust this import based on your actual Button component path

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['row-added']);

const form = reactive({
  eventType: '',
  duration: null,
  date: new Date().toISOString().split('T')[0], // Default to today's date
  description: '',
});

const eventTypes = ref([
  { label: 'Development', value: 'Development' },
  { label: 'Meeting', value: 'Meeting' },
  { label: 'Debugging', value: 'Debugging' },
  { label: 'Documentation', value: 'Documentation' },
  { label: 'Testing', value: 'Testing' },
  { label: 'Support', value: 'Support' },
]);

const isLoading = ref(false);
const timeSheetEntries = ref([]); // To display current entries

// Resource to fetch time sheet entries (you'll need a Frappe API endpoint for this)
const fetchTimeSheet = createResource({
  url: 'helpdesk.helpdesk.doctype.hd_ticket.api.get_time_sheet_entries', // Replace with your actual API endpoint
  auto: true,
  makeParams: () => ({
    ticket_id: props.ticketId,
  }),
  onSuccess: (data) => {
    timeSheetEntries.value = data;
  },
  onError: (error) => {
    toast.error('Failed to fetch time sheet entries: ' + (error.message || 'Unknown error'));
  },
});

const addTimeSheetRow = async () => {
  if (!form.eventType || !form.duration || !form.date) {
    toast.error('Please fill in all required fields.');
    return;
  }

  isLoading.value = true;
  try {
    // Call your Frappe API to add a time sheet entry
    // You'll need to create a Python method in your Frappe app for this
    await call('helpdesk.helpdesk.doctype.hd_ticket.api.add_time_sheet_entry', { // Replace with your actual API endpoint
      ticket_id: props.ticketId,
      event_type: form.eventType,
      duration: form.duration,
      date: form.date,
      description: form.description,
    });
    toast.success('Time sheet entry added successfully!');
    // Clear the form
    form.eventType = '';
    form.duration = null;
    form.description = '';
    emit('row-added'); // Emit event to notify parent to reload ticket data or activities
    fetchTimeSheet.reload(); // Reload the list of entries
  } catch (error) {
    toast.error('Failed to add time sheet entry: ' + (error.message || 'Unknown error'));
  } finally {
    isLoading.value = false;
  }
};

const deleteTimeSheetEntry = async (index) => {
  const entryToDelete = timeSheetEntries.value[index];
  if (!confirm(`Are you sure you want to delete the entry for "${entryToDelete.eventType}" on ${entryToDelete.date}?`)) {
    return;
  }

  try {
    // Call your Frappe API to delete a time sheet entry
    // You'll need to create a Python method for this
    await call('helpdesk.helpdesk.doctype.hd_ticket.api.delete_time_sheet_entry', { // Replace with your actual API endpoint
      entry_id: entryToDelete.name, // Assuming 'name' is the unique ID for the entry
    });
    toast.success('Time sheet entry deleted successfully!');
    fetchTimeSheet.reload(); // Reload the list of entries
    emit('row-added'); // Emit event to notify parent if necessary
  } catch (error) {
    toast.error('Failed to delete time sheet entry: ' + (error.message || 'Unknown error'));
  }
};

onMounted(() => {
  fetchTimeSheet.reload();
});
</script>

<style scoped>
/* Add any specific styles for your form here */
.time-sheet-form {
  max-width: 600px;
  margin: 0 auto;
}
</style>