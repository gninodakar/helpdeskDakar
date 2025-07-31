<template>
  <div class="time-sheet-form p-4 border rounded-md bg-white shadow-sm">
    <h3 class="text-lg font-semibold mb-4 text-gray-800">
      Add Time Sheet Entry
    </h3>
    <div class="flex justify-start mb-4 items-center gap-2">
      <label
        for="reportActions"
        class="text-sm font-medium text-gray-700 sr-only"
        >Report Actions</label
      >
      <select
        id="reportActions"
        v-model="selectedReportAction"
        @change="executeReportAction"
        class="block px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
      >
        <option value="">Select Report Action</option>
        <option value="email">Email Ticket PDF</option>
        <option value="download">Download Report PDF</option>
      </select>
    </div>

    <div class="flex justify-start mb-4"></div>
    <form
      @submit.prevent="addTimeSheetRow"
      class="flex flex-wrap items-end gap-4 mb-8"
    >
      <div class="flex-1 min-w-[150px]">
        <label
          for="eventType"
          class="block text-sm font-medium text-gray-700 mb-1"
          >Event</label
        >
        <select
          id="eventType"
          v-model="form.type_event"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
        >
          <option value="">Select event</option>
          <option
            v-for="event in eventTypes"
            :key="event.value"
            :value="event.value"
          >
            {{ event.event_name }}
          </option>
        </select>
      </div>

      <div class="flex-grow min-w-[100px]">
        <label
          for="duration"
          class="block text-sm font-medium text-gray-700 mb-1"
          >Duration (HH:mm)</label
        >
        <input
          type="time"
          id="duration"
          data-fieldtype="Time"
          data-fieldname="duration"
          v-model="form.durationTime"
          class="form-control block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
        />
      </div>

      <div class="flex-grow min-w-[150px]">
        <label for="date" class="block text-sm font-medium text-gray-700 mb-1"
          >Date</label
        >
        <input
          type="date"
          id="date"
          v-model="form.date"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
        />
      </div>

      <div class="flex-auto min-w-[200px]">
        <label
          for="description"
          class="block text-sm font-medium text-gray-700 mb-1"
          >Description</label
        >
        <textarea
          id="description"
          v-model="form.hd_event_description"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Optional notes..."
          rows="3"
          required
        ></textarea>
      </div>
      <div class="flex-shrink-0">
        <button
          type="submit"
          :disabled="isLoading"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          :class="{ 'opacity-50 cursor-not-allowed': isLoading }"
        >
          {{ isLoading ? "Adding..." : "Add Entry" }}
        </button>
      </div>
    </form>
    <div
      v-if="timeSheetEntries.length"
      class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-800 flex justify-between items-center"
    >
      <span class="font-semibold">Total Time Expended:</span>
      <span class="text-xl font-bold">{{ totalDuration }} hours</span>
    </div>

    <div v-if="timeSheetEntries.length" class="mt-8">
      <h4 class="text-md font-semibold mb-3 text-gray-800">
        Current Time Sheet Entries
      </h4>
      <div class="overflow-x-auto border border-gray-200 rounded-md">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                ID
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Agent
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Event
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                (hrs)
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Date
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Description
              </th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="entry in timeSheetEntries" :key="entry.name">
              <td
                class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
              >
                {{ entry.id }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
              >
                {{ entry.agent }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
              >
                {{ entry.type_event }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ entry.duration }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ entry.date }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-600 max-w-xs">
                {{ entry.hd_event_description || "-" }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
              >
                <button
                  type="button"
                  @click="deleteTimeSheetEntry(entry)"
                  class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  title="Delete Entry"
                >
                  <FeatherIcon name="trash-2" class="h-5 w-5" />
                  <span class="sr-only">Delete</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div
      v-else
      class="mt-8 p-4 text-center text-gray-500 border border-dashed rounded-md"
    >
      No time sheet entries added yet.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { call, toast, createResource, dayjs } from "frappe-ui";

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["row-added"]);

const form = reactive({
  type_event: "",
  durationTime: null,
  date: new Date().toISOString().split("T")[0],
  hd_event_description: "",
});

const isLoading = ref(false);
const timeSheetEntries = ref<any[]>([]);

// dummy data for testing
const dummyTimeSheetEntries = [];

const totalDuration = computed(() => {
  return timeSheetEntries.value
    .reduce((sum, entry) => {
      return sum + (typeof entry.duration === "number" ? entry.duration : 0);
    }, 0)
    .toFixed(1);
});

const selectedReportAction = ref("");

const executeReportAction = () => {
  if (selectedReportAction.value === "email") {
    sendTicketpdf();
  } else if (selectedReportAction.value === "download") {
    downloadpdf();
  }
  //reset action
  selectedReportAction.value = "";
};

/* ******************************** */
// send pdf data
/* ******************************** */
const sendTicketpdf = async () => {
  const recipients = ["guillermo@albanss.com"];
  const pdfTitle = "My Personalised Notes";
  const customText = "This is a proof text for the PDF.";
  const senderEmail = "ganpforrest@gmail.com";

  try {
    await call("helpdesk.api.ticket_time_sheet.send_report_pdf", {
      recipients: recipients,
      pdf_title: pdfTitle,
      pdf_text_content: customText,
      sender_email_address: senderEmail,
    });

    toast.success("Email with personalised PDF successfully sent.");
  } catch (error) {
    console.error("Error when sending mail with PDF:", error);
    const errorMessage = error.messages
      ? error.messages.join(", ")
      : error.message || "Unknown error";
    toast.error("Error when sending mail with PDF: " + errorMessage);
  }
};

/* ******************************** */
// download pdf data
/* ******************************** */
const downloadpdf = async () => {
  try {
    // Replace with your actual Frappe API call for downloading PDF
    // This example assumes it returns a file URL or triggers a download
    const response = await call(
      "helpdesk.api.ticket_time_sheet.download_report_pdf",
      {
        ticket_id: props.ticketId, // Pass any necessary parameters
      }
    );

    // Example if the API returns a downloadable URL:
    if (response && response.file_url) {
      window.open(response.file_url, "_blank");
      toast.success("PDF download initiated!");
    } else {
      toast.info(
        "Download request sent. Check your browser's download manager."
      );
    }
  } catch (error) {
    console.error("Error downloading PDF:", error);
    const errorMessage = error.messages
      ? error.messages.join(", ")
      : error.message || "Unknown error";
    toast.error("Failed to download PDF: " + errorMessage);
  }
};

/* ******************************** */
// NEW RESOURCE TO FETCH EVENT TYPE NAMES
/* ******************************** */
const eventTypesResource = createResource({
  url: "helpdesk.api.ticket_time_sheet.get_event_type_names",
  auto: true,
  onSuccess: (data) => {
    eventTypes.value = Array.isArray(data) ? data : [];
  },
  onError: (error) => {
    console.error("Failed to fetch event types:", error);
    toast.error("Failed to load event types.");
    // Fallback to static dummy list if API fails
    eventTypes.value = [
      { label: "Development", value: "Development" },
      { label: "Meeting", value: "Meeting" },
      { label: "Debugging", value: "Debugging" },
      { label: "Documentation", value: "Documentation" },
      { label: "Testing", value: "Testing" },
      { label: "Support", value: "Support" },
      { label: "Other", value: "Other" },
    ];
  },
});
const eventTypes = ref([]); // Initialize as empty array, will be filled by eventTypesResource

/* ******************************** */
// Fetch ticket events
/* ******************************** */
const fetchTimeSheet = createResource({
  url: "helpdesk.api.ticket_time_sheet.get_events",
  auto: true,
  makeParams: () => ({
    ticket_id: props.ticketId,
  }),
  onSuccess: (data) => {
    if (!Array.isArray(data) || data.length === 0) {
      console.warn("API returned no time sheet entries");
      timeSheetEntries.value = dummyTimeSheetEntries;
    } else {
      timeSheetEntries.value = data.map((entry) => ({
        id: entry.tts_id,
        agent: entry.tts_agent,
        type_event: entry.tts_event_type,
        duration: entry.tts_event_duration,
        date: entry.tts_event_date,
        hd_event_description: entry.tts_event_description,
      }));
    }
  },
  onError: (error) => {
    console.error(
      "Failed to fetch time sheet entries from API. Using dummy data.",
      error
    );
    toast.error(
      "Failed to fetch time sheet entries: " +
        (error.messages
          ? error.messages.join(", ")
          : error.message || "Unknown error")
    );
    timeSheetEntries.value = dummyTimeSheetEntries;
  },
});

/* ******************************** */
// Add new event to ticket
/* ******************************** */
const addTimeSheetRow = async () => {
  if (
    !form.type_event ||
    !form.durationTime ||
    !form.date ||
    !form.hd_event_description
  ) {
    toast.error(
      "Please fill in all required fields correctly (Duration must be mayor 0)."
    );
    return;
  }

  isLoading.value = true;

  try {
    let dateToSend = dayjs(form.date).format("YYYY-MM-DD");

    await call("helpdesk.api.ticket_time_sheet.add_time_sheet_entry", {
      ticket_id: props.ticketId,
      event_type_name: form.type_event,
      duration: form.durationTime,
      date: dateToSend,
      description: form.hd_event_description,
    });

    toast.success("Time sheet entry added successfully!");
    // Clear the form
    form.type_event = "";
    form.durationTime = null;
    form.hd_event_description = "";
    form.date = new Date().toISOString().split("T")[0]; // Reset date to today

    emit("row-added");
    fetchTimeSheet.reload(); // Reload the list of entries
  } catch (error) {
    console.error("Error adding time sheet entry:", error);
    const errorMessage = error.messages
      ? error.messages.join(", ")
      : error.message || "Unknown error";
    toast.error("Failed to add time sheet entry: " + errorMessage);
  } finally {
    isLoading.value = false;
  }
};

/* ******************************** */
// Delete event ticket
/* ******************************** */

const deleteTimeSheetEntry = async (entry: any) => {
  if (!entry || !entry.id) {
    toast.error("Cannot delete entry: Missing ID.");
    return;
  }

  // IMPORTANT: Use new fieldname for confirm message
  if (
    !confirm(
      `Are you sure you want to delete the entry ID: "${entry.id}" on ${entry.date}?`
    )
  ) {
    return;
  }

  try {
    if (entry.id && String(entry.id).startsWith("dummy-")) {
      console.warn(
        `Attempted to delete dummy entry: ${entry.id}. Not calling API.`
      );
      timeSheetEntries.value = timeSheetEntries.value.filter(
        (e) => e.id !== entry.id
      );
      toast.success("Dummy time sheet entry deleted locally!");
      return;
    }

    await call("helpdesk.api.ticket_time_sheet.delete_time_sheet_entry", {
      tts_id: entry.id,
    });
    toast.success("Time sheet entry deleted successfully!");
    fetchTimeSheet.reload();
    emit("row-added");
  } catch (error) {
    console.error("Error deleting time sheet entry:", error);
    const errorMessage = error.messages
      ? error.messages.join(", ")
      : error.message || "Unknown error";
    toast.error("Failed to delete time sheet entry: " + errorMessage);
  }
};

onMounted(() => {
  fetchTimeSheet.reload();
  eventTypesResource.reload(); // Trigger fetching event types on mount
});
</script>

<!-- ************************* 
 styles 
<!-- ************************ -->
<style scoped>
/* Basic styling for the form elements */
label {
  display: block;
  margin-bottom: 0.25rem;
}

input[type="text"],
input[type="number"],
input[type="date"],
select {
  padding: 0.5rem 0.75rem;
  border-width: 1px;
  border-color: #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  width: 100%;
}

.custom-select-width {
  width: auto;
  min-width: 150px;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  ring-width: 2px;
  ring-color: #3b82f6;
  border-color: #3b82f6;
}

/* Table specific styling - Tailwind classes are quite verbose, but effective */
table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.5rem 1.5rem;
  text-align: left;
}

thead th {
  background-color: #f9fafb;
  border-bottom-width: 1px;
  border-color: #e5e7eb;
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

tbody td {
  border-bottom-width: 1px;
  border-color: #e5e7eb;
}

tbody tr:last-child td {
  border-bottom: none;
}
</style>
