<template>
  <div class="time-sheet-form p-4 border rounded-md bg-white shadow-sm">
    <h3 class="text-lg font-semibold mb-4 text-gray-800">
      Add Time Sheet Entry
    </h3>
    <div class="flex flex-col sm:flex-row justify-start mb-4 gap-2">
      <button
        class="rounded bg-teal-500 px-3 py-1.5 text-base font-medium text-white hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2"
        @click="sendmailpdf" title="Email Ticket as PDF">
        Email Time Sheet
      </button>
      <button
        class="rounded bg-amber-600 px-3 py-1.5 text-base font-medium text-white hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2"
        @click="downloadPdfDirect" title="Download Report">
        Download Time Sheet
      </button>
    </div>
    <form @submit.prevent="addTimeSheetRow" class="flex flex-wrap items-end gap-4 mb-8">
      <div class="flex-1 min-w-[150px]">
        <label for="eventType" class="block text-sm font-medium text-gray-700 mb-1">Work Type</label>
        <select id="eventType" v-model="form.type_event"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required>
          <option value="">Select event</option>
          <option v-for="event in eventTypes" :key="event.value" :value="event.value">
            {{ event.event_name }}
          </option>
        </select>
      </div>

      <div class="flex-grow min-w-[100px]">
        <label for="duration" class="block text-sm font-medium text-gray-700 mb-1">Duration (HH:mm)</label>
        <div class="relative">
          <input type="text" id="duration" v-model="form.durationTime" @input="formatTimeInput" @blur="
            () => {
              if (form.durationTime && !validateTime(form.durationTime))
                toast.error('Invalid time: hours 0-99, minutes 0-59');
            }
          " class="form-control block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="00:00" maxlength="5" required />
          <button v-if="form.durationTime" type="button" @click="clearDuration"
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="flex-grow min-w-[150px]">
        <label for="date" class="block text-sm font-medium text-gray-700 mb-1">Date</label>
        <input type="date" id="date" v-model="form.date"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required />
      </div>

      <div class="flex-auto min-w-[200px]">
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea id="description" v-model="form.hd_event_description"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Optional notes..." rows="3" required></textarea>
      </div>
      <div class="flex-shrink-0">
        <button type="submit" :disabled="isLoading"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          :class="{ 'opacity-50 cursor-not-allowed': isLoading }">
          {{ isLoading ? "Adding..." : "Add Entry" }}
        </button>
      </div>
    </form>
    <div v-if="timeSheetEntries.length"
      class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-800 flex justify-between items-center">
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
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Agent
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Work Type
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                (hrs)
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
                {{ entry.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ entry.agent }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
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
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button type="button" @click="deleteTimeSheetEntry(entry)"
                  class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  title="Delete Entry">
                  <FeatherIcon name="trash-2" class="h-5 w-5" />
                  <span class="sr-only">Delete</span>
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
import { ref, reactive, onMounted, nextTick } from "vue";
import { call, toast, createResource, dayjs } from "frappe-ui";

// dummy data for testing
const dummyTimeSheetEntries = [];

///
const validateAndCorrectTime = (timeString: string): string => {
  if (!timeString) {
    return "";
  }

  // If it's already in HH:mm format, validate and correct
  if (timeString.length === 5 && timeString[2] === ":") {
    const [hours, minutes] = timeString.split(":");
    const hoursNum = parseInt(hours, 10);
    const minutesNum = parseInt(minutes, 10);

    if (!isNaN(hoursNum) && !isNaN(minutesNum)) {
      // Validate hours (0-99)
      const correctedHours = Math.max(0, Math.min(99, hoursNum));

      // Correct minutes if over 59
      const correctedMinutes = Math.min(59, Math.max(0, minutesNum));

      // Format with leading zeros
      return `${correctedHours.toString().padStart(2, "0")}:${correctedMinutes
        .toString()
        .padStart(2, "0")}`;
    }
  }

  return timeString;
};

const validateTime = (timeString: string): boolean => {
  if (!timeString || timeString.length !== 5 || timeString[2] !== ":") {
    return false;
  }

  const [hours, minutes] = timeString.split(":");
  const hoursNum = parseInt(hours, 10);
  const minutesNum = parseInt(minutes, 10);

  // Validate hours (0-99) and minutes (0-59)
  return (
    !isNaN(hoursNum) &&
    !isNaN(minutesNum) &&
    hoursNum >= 0 &&
    hoursNum <= 99 &&
    minutesNum >= 0 &&
    minutesNum <= 59
  );
};

//
const clearDuration = (): void => {
  form.durationTime = "";
  // Optional: focus the input after clearing
  nextTick(() => {
    const durationInput = document.getElementById("duration");
    if (durationInput) {
      durationInput.focus();
    }
  });
};

// Function to format time input as HH:mm
const formatTimeInput = (event) => {
  let value = event.target.value.replace(/[^0-9]/g, "");

  // Allow empty value (for clearing)
  if (value.length === 0) {
    form.durationTime = "";
    return;
  }

  if (value.length > 4) {
    value = value.slice(0, 4);
  }

  if (value.length > 2) {
    value = value.slice(0, 2) + ":" + value.slice(2, 4);
    // Auto-correct if minutes are over 59
    value = validateAndCorrectTime(value);
  }

  form.durationTime = value;
};

//props
const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
});

//emit
const emit = defineEmits(["row-added"]);
const form = reactive({
  type_event: "",
  durationTime: null,
  date: new Date().toISOString().split("T")[0],
  hd_event_description: "",
});

const isLoading = ref(false);
const timeSheetEntries = ref<any[]>([]);
const totalDuration = ref("00:00");

/* ******************************** */
// donwload pdf
/* ******************************** */
const downloadPdfDirect = async () => {
  try {
    const functionPath = "helpdesk.api.ticket_time_sheet.download_report_pdf";
    const params = new URLSearchParams({
      ticket_id: props.ticketId,
    });

    const url = `/api/method/${functionPath}?${params.toString()}`;

    // Create temporary link and trigger download
    const link = document.createElement("a");
    link.href = url;
    link.download = `timesheet-report-${props.ticketId || "report"}-${new Date().toISOString().split("T")[0]
      }.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Show success toast
    toast.success("PDF report download started successfully!");
  } catch (error) {
    console.error("PDF download failed:", error);
    toast.error(
      "Failed to download PDF report: " + (error.message || "Unknown error")
    );
  }
};

/* ******************************** */
// send email pdf data
/* ******************************** */
const sendmailpdf = async () => {
  const recipients = ["guillermo@albanss.com"];
  const pdfTitle = "My Personalised Notes";
  const customText = "This is a proof text for the PDF.";
  const senderEmail = "ganpforrest@gmail.com";

  try {
    await call("helpdesk.api.ticket_time_sheet.send_report_pdf", {
      ticket_id: props.ticketId,
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
    console.log("here the data", data);
    if (!Array.isArray(data.events) || data.length === 0) {
      console.warn("API returned no time sheet entries");
      timeSheetEntries.value = dummyTimeSheetEntries;
    } else {
      timeSheetEntries.value = data.events.map((entry) => ({
        id: entry.tts_id,
        agent: entry.tts_agent,
        type_event: entry.tts_event_type,
        duration: entry.tts_event_duration,
        date: entry.tts_event_date,
        hd_event_description: entry.tts_event_description,
      }));
    }

    //udpate time spent label
    if (data.total_time_spent !== undefined) {
      totalDuration.value = data.total_time_spent;
    } else {
      totalDuration.value = "00:00";
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
    form.date = new Date().toISOString().split("T")[0];

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

// onMounted(() => {
//   fetchTimeSheet.reload();
//   eventTypesResource.reload(); // Trigger fetching event types on mount
// });
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
