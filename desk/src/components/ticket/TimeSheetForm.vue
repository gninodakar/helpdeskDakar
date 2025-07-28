<template>
  <div class="time-sheet-form p-4 border rounded-md bg-white shadow-sm">
    <h3 class="text-lg font-semibold mb-4 text-gray-800">Add Time Sheet Entry</h3>

    <form @submit.prevent="addTimeSheetRow" class="flex flex-wrap items-end gap-4 mb-8">
      <div class="flex-1 min-w-[150px]">
        <label for="eventType" class="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
        <select
          id="eventType"
          v-model="form.hd_event_ts_name" class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
        >
          <option value="">Select event</option>
          <option v-for="event in eventTypes" :key="event.value" :value="event.value">
            {{ event.event_name }}
          </option>
        </select>
      </div>

      <div class="flex-grow min-w-[100px]">
        <label for="duration" class="block text-sm font-medium text-gray-700 mb-1">Duration (hours)</label>
        <input
          type="number"
          id="duration"
          v-model.number="form.duration"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          min="0.1"
          step="0.1"
          required
        />
      </div>

      <div class="flex-grow min-w-[150px]">
        <label for="date" class="block text-sm font-medium text-gray-700 mb-1">Date</label>
        <input
          type="date"
          id="date"
          v-model="form.date"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
        />
      </div>

      <div class="flex-auto min-w-[200px]">
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <input
          type="text"
          id="description"
          v-model="form.hd_event_description" class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Optional notes..."
        />
      </div>

      <div class="flex-shrink-0">
        <button
          type="submit"
          :disabled="isLoading"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          :class="{ 'opacity-50 cursor-not-allowed': isLoading }"
        >
          {{ isLoading ? 'Adding...' : 'Add Entry' }}
        </button>
      </div>
    </form>

    <div v-if="timeSheetEntries.length" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-800 flex justify-between items-center">
      <span class="font-semibold">Total Time Expended:</span>
      <span class="text-xl font-bold">{{ totalDuration }} hours</span>
    </div>

    <div v-if="timeSheetEntries.length" class="mt-8">
      <h4 class="text-md font-semibold mb-3 text-gray-800">Current Time Sheet Entries</h4>
      <div class="overflow-x-auto border border-gray-200 rounded-md">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Event Type
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duration (hrs)
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="entry in timeSheetEntries" :key="entry.name">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ entry.hd_event_ts_name }} </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ entry.duration }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ entry.date }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600 max-w-xs">
                {{ entry.hd_event_description || '-' }} </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  type="button"
                  @click="deleteTimeSheetEntry(entry)"
                  class="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="mt-8 p-4 text-center text-gray-500 border border-dashed rounded-md">
      No time sheet entries added yet.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { call, toast, createResource } from 'frappe-ui';

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['row-added']);

const form = reactive({
  // IMPORTANT: Changed these to match your DocType fieldnames
  hd_event_ts_name: '',
  duration: null,
  date: new Date().toISOString().split('T')[0],
  hd_event_description: '', // IMPORTANT: Changed this to match your DocType fieldname
});

// REMOVE THE STATIC EVENT TYPES ARRAY
// const eventTypes = ref([
//   { label: 'Development', value: 'Development' },
//   // ... other static types
// ]);

const isLoading = ref(false);
const timeSheetEntries = ref<any[]>([]);

const dummyTimeSheetEntries = [
  // IMPORTANT: Updated dummy data to match new fieldnames
  {
    name: 'dummy-1',
    hd_event_ts_name: 'Development',
    duration: 3.5,
    date: '2025-07-23',
    hd_event_description: 'Working on feature X for ticket #' + props.ticketId,
  },
  {
    name: 'dummy-2',
    hd_event_ts_name: 'Meeting',
    duration: 1.0,
    date: '2025-07-24',
    hd_event_description: 'Daily stand-up with team',
  },
  {
    name: 'dummy-3',
    hd_event_ts_name: 'Debugging',
    duration: 2.0,
    date: '2025-07-25',
    hd_event_description: 'Investigated bug in login module',
  },
];

const totalDuration = computed(() => {
  return timeSheetEntries.value.reduce((sum, entry) => {
    return sum + (typeof entry.duration === 'number' ? entry.duration : 0);
  }, 0).toFixed(1);
});

// *** NEW RESOURCE TO FETCH EVENT TYPE NAMES ***
const eventTypesResource = createResource({
    url: 'helpdesk.api.ticket_time_sheet.get_event_type_names', // Path to your new API method
    auto: true,
    onSuccess: (data) => {        
        eventTypes.value = Array.isArray(data) ? data : [];
    },
    onError: (error) => {
        console.error("Failed to fetch event types:", error);
        toast.error('Failed to load event types.');
        // Fallback to static dummy list if API fails
        eventTypes.value = [
            { label: 'Development', value: 'Development' },
            { label: 'Meeting', value: 'Meeting' },
            { label: 'Debugging', value: 'Debugging' },
            { label: 'Documentation', value: 'Documentation' },
            { label: 'Testing', value: 'Testing' },
            { label: 'Support', value: 'Support' },
            { label: 'Other', value: 'Other' },
        ];
    }
});
const eventTypes = ref([]); // Initialize as empty array, will be filled by eventTypesResource

// Resource to fetch time sheet entries (modified to match new fieldnames)
const fetchTimeSheet = createResource({
  url: 'helpdesk.api.ticket_time_sheet.get_events',
  auto: true,
  makeParams: () => ({
    ticket_id: props.ticketId,
  }),
  onSuccess: (data) => {
    if (!Array.isArray(data) || data.length === 0) {
      console.warn("API returned no time sheet entries");
      timeSheetEntries.value = dummyTimeSheetEntries;
    } else {
      timeSheetEntries.value = data.map(entry => ({
      hd_event_ts_name: entry.event_type,    
      duration: entry.event_duration,
      date: entry.event_date,
      hd_event_description: entry.event_description,        
      }));
    }
  },
  onError: (error) => {
    console.error("Failed to fetch time sheet entries from API. Using dummy data.", error);
    toast.error('Failed to fetch time sheet entries: ' + (error.messages ? error.messages.join(", ") : error.message || 'Unknown error'));
    timeSheetEntries.value = dummyTimeSheetEntries;
  },
});

const addTimeSheetRow = async () => {
  // IMPORTANT: Changed form field references to match new names
  if (!form.hd_event_ts_name || form.duration === null || form.duration <= 0 || !form.date) {
    toast.error('Please fill in all required fields correctly (Duration must be > 0).');
    return;
  }

  isLoading.value = true;
  try {
    await call('helpdesk.api.add_time_sheet_entry', {
      ticket_id: props.ticketId,
      event_type: form.hd_event_ts_name, // Pass the value from the updated form field
      duration: form.duration,
      date: form.date,
      description: form.hd_event_description, // Pass the value from the updated form field
    });

    toast.success('Time sheet entry added successfully!');
    // Clear the form - IMPORTANT: Use new fieldnames here
    form.hd_event_ts_name = '';
    form.duration = null;
    form.hd_event_description = '';
    form.date = new Date().toISOString().split('T')[0]; // Reset date to today

    emit('row-added');
    fetchTimeSheet.reload(); // Reload the list of entries
  } catch (error) {
    console.error("Error adding time sheet entry:", error);
    const errorMessage = error.messages ? error.messages.join(", ") : (error.message || 'Unknown error');
    toast.error('Failed to add time sheet entry: ' + errorMessage);
  } finally {
    isLoading.value = false;
  }
};

const deleteTimeSheetEntry = async (entry: any) => {
  if (!entry || !entry.name) {
    toast.error("Cannot delete entry: Missing ID.");
    return;
  }

  // IMPORTANT: Use new fieldname for confirm message
  if (!confirm(`Are you sure you want to delete the entry for "${entry.hd_event_ts_name}" on ${entry.date}?`)) {
    return;
  }

  try {
    if (entry.name && String(entry.name).startsWith('dummy-')) {
        console.warn(`Attempted to delete dummy entry: ${entry.name}. Not calling API.`);
        timeSheetEntries.value = timeSheetEntries.value.filter(e => e.name !== entry.name);
        toast.success('Dummy time sheet entry deleted locally!');
        return;
    }

    await call('helpdesk.api.delete_time_sheet_entry', {
      entry_id: entry.name,
    });
    toast.success('Time sheet entry deleted successfully!');
    fetchTimeSheet.reload();
    emit('row-added');
  } catch (error) {
    console.error("Error deleting time sheet entry:", error);
    const errorMessage = error.messages ? error.messages.join(", ") : (error.message || 'Unknown error');
    toast.error('Failed to delete time sheet entry: ' + errorMessage);
  }
};

onMounted(() => {
  fetchTimeSheet.reload();
  eventTypesResource.reload(); // Trigger fetching event types on mount
});
</script>

<style scoped>
/* Your existing styles remain here */
.time-sheet-form {
  /* padding, border, bg-white, shadow-sm are kept from your original */
}

/* Basic styling for the form elements */
label {
  display: block;
  margin-bottom: 0.25rem; /* Tailwind: mb-1 */
}

input[type="text"],
input[type="number"],
input[type="date"],
select {
  padding: 0.5rem 0.75rem; /* Tailwind: px-3 py-2 */
  border-width: 1px;
  border-color: #d1d5db; /* Tailwind: border-gray-300 */
  border-radius: 0.375rem; /* Tailwind: rounded-md */
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* Tailwind: shadow-sm */
  width: 100%;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  ring-width: 2px;
  ring-color: #3b82f6; /* Tailwind: focus:ring-blue-500 */
  border-color: #3b82f6; /* Tailwind: focus:border-blue-500 */
}

/* Table specific styling - Tailwind classes are quite verbose, but effective */
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem 1.5rem; /* Tailwind: px-6 py-4 for td, px-6 py-3 for th */
  text-align: left;
}

thead th {
  background-color: #f9fafb; /* Tailwind: bg-gray-50 */
  border-bottom-width: 1px;
  border-color: #e5e7eb; /* Tailwind: border-gray-200 */
  font-size: 0.75rem; /* Tailwind: text-xs */
  font-weight: 500; /* Tailwind: font-medium */
  color: #6b7280; /* Tailwind: text-gray-500 */
  text-transform: uppercase;
  letter-spacing: 0.05em; /* Tailwind: tracking-wider */
}

tbody td {
  border-bottom-width: 1px;
  border-color: #e5e7eb; /* Tailwind: divide-y divide-gray-200 on tbody parent */
}

tbody tr:last-child td {
  border-bottom: none;
}
</style>