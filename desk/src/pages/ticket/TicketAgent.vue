<template>
  <div class="flex flex-col">
    <LayoutHeader v-if="ticket.data">
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" class="breadcrumbs">
          <template #prefix="{ item }">
            <Icon v-if="item.icon" :icon="item.icon" class="mr-1 h-4 flex items-center justify-center self-center" />
          </template>
        </Breadcrumbs>
      </template>
      <template #right-header>
        <CustomActions v-if="ticket.data._customActions" :actions="ticket.data._customActions" />
        <div v-if="ticket.data.assignees?.length">
          <component :is="ticket.data.assignees.length == 1 ? 'Button' : 'div'">
            <MultipleAvatar :avatars="ticket.data.assignees" @click="showAssignmentModal = true" />
          </component>
        </div>
        <button v-else class="rounded bg-gray-100 px-2 py-1.5 text-base text-gray-800"
          @click="showAssignmentModal = true">
          Assign
        </button>
        <Dropdown :options="dropdownOptions">
          <template #default="{ open }">
            <Button :label="ticket.data.status">
              <template #prefix>
                <IndicatorIcon :class="ticketStatusStore.textColorMap[ticket.data.status]" />
              </template>
              <template #suffix>
                <FeatherIcon :name="open ? 'chevron-up' : 'chevron-down'" class="h-4" />
              </template>
            </Button>
          </template>
        </Dropdown>
      </template>
    </LayoutHeader>
    <div v-if="ticket.data" class="flex h-full overflow-hidden">
      <div class="flex flex-1 flex-col max-w-[calc(100%-382px)]">
        <div class="overflow-y-hidden flex flex-1 !h-full flex-col">
          <Tabs v-model="tabIndex" :tabs="tabs">
            <TabList />
            <TabPanel v-slot="{ tab }" class="h-full">
              <TicketAgentActivities v-if="tab.name !== 'timeSheet'" ref="ticketAgentActivitiesRef"
                :activities="filterActivities(tab.name)" :title="tab.label" :ticket-status="ticket.data?.status"
                @update="
                  () => {
                    ticket.reload();
                  }
                " @email:reply="
                  (e) => {
                    communicationAreaRef.replyToEmail(e);
                  }
                " />
              <div v-else-if="tab.name === 'timeSheet'" class="p-4 h-full overflow-y-auto">
                <TimeSheetForm :ticket-id="ticket.data.name" @row-added="ticket.reload()" />
              </div>
            </TabPanel>
          </Tabs>
        </div>
        <CommunicationArea v-if="tabs[tabIndex].name !== 'timeSheet'" ref="communicationAreaRef" v-model="ticket.data"
          :to-emails="[ticket.data?.raised_by]" :cc-emails="[]" :bcc-emails="[]" :key="ticket.data?.name" @update="
            () => {
              ticket.reload();
              ticketAgentActivitiesRef.scrollToLatestActivity();
            }
          " />
      </div>
      <TicketAgentSidebar :ticket="ticket.data" @update="({ field, value }) => updateTicket(field, value)"
        @email:open="(e) => communicationAreaRef.toggleEmailBox()" @reload="ticket.reload()" />
    </div>
    <AssignmentModal v-if="ticket.data" v-model="showAssignmentModal" :assignees="ticket.data.assignees"
      :docname="ticketId" doctype="HD Ticket" @update="
        () => {
          ticket.reload();
        }
      " />
    <Dialog v-model="showSubjectDialog" :options="{ title: 'Rename Subject' }">
      <template #body-content>
        <div class="flex flex-col flex-1 gap-3">
          <FormControl v-model="renameSubject" type="textarea" size="sm" variant="subtle" :disabled="false" />
          <Button variant="solid" :loading="isLoading" label="Rename" @click="handleRename" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import {
  Breadcrumbs,
  Dialog,
  Dropdown,
  FormControl,
  TabList,
  TabPanel,
  Tabs,
  call,
  createResource,
  toast,
} from "frappe-ui";
import { computed, h, onMounted, onUnmounted, provide, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  AssignmentModal,
  CommunicationArea,
  Icon,
  LayoutHeader,
  MultipleAvatar,
} from "@/components";
import {
  ActivityIcon,
  CommentIcon,
  EmailIcon,
  IndicatorIcon,
} from "@/components/icons";

import { TicketAgentActivities, TicketAgentSidebar } from "@/components/ticket";
import TimeSheetForm from "@/components/ticket/TimeSheetForm.vue";
import { setupCustomizations } from "@/composables/formCustomisation";
import { useView } from "@/composables/useView";
import { socket } from "@/socket";
import { globalStore } from "@/stores/globalStore";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { useUserStore } from "@/stores/user";
import { TabObject, TicketTab, View } from "@/types";
import { getIcon } from "@/utils";
import { ComputedRef } from "vue";
import { showAssignmentModal } from "./modalStates";
import TimeSheetIcon from "@/components/icons/timeSheetIcon.vue";
const route = useRoute();
const router = useRouter();

const ticketStatusStore = useTicketStatusStore();
const { getUser } = useUserStore();
const { $dialog } = globalStore();
const ticketAgentActivitiesRef = ref(null);
const communicationAreaRef = ref(null);
const renameSubject = ref("");
const isLoading = ref(false);

const props = defineProps({
  ticketId: { type: String, required: true },
  fromLabel: { type: String, default: 'Tickets' },
  fromRoute: { type: String, default: 'TicketsAgent' },
  fromPath: { type: String, default: null }, // ← new property
})

watch(
  () => props.ticketId,
  () => {
    ticket.reload();
  }
);


const { findView } = useView("HD Ticket");

provide("communicationArea", communicationAreaRef);

const showSubjectDialog = ref(false);

const ticket = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.get_one",
  auto: true,
  makeParams: () => ({
    name: props.ticketId,
  }),
  transform: (data) => {
    if (data._assign) {
      data.assignees = JSON.parse(data._assign).map((assignee) => {
        return {
          name: assignee,
          image: getUser(assignee).user_image,
          label: getUser(assignee).full_name,
        };
      });
    }
    renameSubject.value = data.subject;
  },
  onSuccess: (data) => {
    // console.log(data);
    document.title = data.subject;
    setupCustomizations(ticket, {
      doc: data,
      call,
      router,
      toast,
      $dialog,
      updateField,
      createToast: toast.create,
    });
  },
});
function updateField(name: string, value: string, callback = () => { }) {
  updateTicket(name, value);
  callback();
}


const breadcrumbs = computed(() => {
  const items: any[] = []

  // Item padre: prioriza volver por path exacto (mantiene filtros)
  items.push({
    label: props.fromLabel,
    // si tu <Breadcrumbs> soporta to/route, puedes añadirlo:
    to: props.fromPath ?? { name: props.fromRoute },
    // y garantizamos navegación aunque el componente no lo maneje:
    onClick: () => {
      if (props.fromPath) router.push(props.fromPath)
      else router.push({ name: props.fromRoute })
    },
  })

  // Si usabas el fallback por view en query, puedes mantenerlo opcionalmente:
  // (solo se ejecutaría si NO usas el bloque anterior)
  // ...

  // Último breadcrumb: ticket actual (no navegable)
  items.push({
    label: ticket.data?.subject || `Ticket ${props.ticketId}`,
    onClick: () => { showSubjectDialog.value = true },
  })

  return items
})


const handleRename = () => {
  if (renameSubject.value === ticket.data?.subject) return;
  updateTicket("subject", renameSubject.value);
  showSubjectDialog.value = false;
};

const dropdownOptions = computed(() =>
  ticketStatusStore.options.map((o) => ({
    label: o,
    value: o,
    onClick: () => updateTicket("status", o),
    icon: () =>
      h(IndicatorIcon, {
        class: ticketStatusStore.textColorMap[o],
      }),
  }))
);

// watch(
//   () => ticket.data,
//   (val) => {
//     console.log("CUSTOM ACTIONSSS");
//     // console.log(val._customActions);
//   },
//   { deep: true }
// );

const tabIndex = ref(0);
const tabs: TabObject[] = [
  {
    name: "activity",
    label: "Activity",
    icon: ActivityIcon,
  },
  {
    name: "email",
    label: "Emails",
    icon: EmailIcon,
  },
  {
    name: "comment",
    label: "Comments",
    icon: CommentIcon,
  },
  {
    name: "timeSheet",
    label: "Time Sheet",
    icon: TimeSheetIcon,
  },
];

const activities = computed(() => {
  const emailProps = ticket.data.communications.map((email, idx: number) => {
    return {
      subject: email.subject,
      content: email.content,
      sender: { name: email.user.email, full_name: email.user.name },
      to: email.recipients,
      type: "email",
      key: email.creation,
      cc: email.cc,
      bcc: email.bcc,
      creation: email.communication_date || email.creation,
      attachments: email.attachments,
      name: email.name,
      isFirstEmail: idx === 0,
    };
  });

  const commentProps = ticket.data.comments.map((comment) => {
    return {
      name: comment.name,
      type: "comment",
      key: comment.creation,
      commentedBy: comment.commented_by,
      commenter: comment.user.name,
      creation: comment.creation,
      content: comment.content,
      attachments: comment.attachments,
    };
  });

  const historyProps = [...ticket.data.history, ...ticket.data.views].map(
    (h) => {
      return {
        type: "history",
        key: h.creation,
        content: h.action ? h.action : "viewed this",
        creation: h.creation,
        user: h.user.name + " ",
      };
    }
  );

  const sorted = [...emailProps, ...commentProps, ...historyProps].sort(
    (a, b) => new Date(a.creation).getTime() - new Date(b.creation).getTime()
  );

  const data = [];
  let i = 0;

  while (i < sorted.length) {
    const currentActivity = sorted[i];
    if (currentActivity.type === "history") {
      currentActivity.relatedActivities = [currentActivity];
      for (let j = i + 1; j < sorted.length + 1; j++) {
        const nextActivity = sorted[j];

        if (nextActivity && nextActivity.user === currentActivity.user) {
          currentActivity.relatedActivities.push(nextActivity);
        } else {
          data.push(currentActivity);
          i = j - 1;
          break;
        }
      }
    } else {
      data.push(currentActivity);
    }
    i++;
  }
  return data;
});

function filterActivities(eventType: TicketTab) {
  if (eventType === "activity") {
    return activities.value;
  }
  return activities.value.filter((activity) => activity.type === eventType);
}
const isErrorTriggered = ref(false);
function updateTicket(fieldname: string, value: string) {
  isErrorTriggered.value = false;
  if (value === ticket.data[fieldname]) return;
  updateOptimistic(fieldname, value);

  createResource({
    url: "frappe.client.set_value",
    params: {
      doctype: "HD Ticket",
      name: props.ticketId,
      fieldname,
      value,
    },
    debounce: 500,
    auto: true,
    onSuccess: () => {
      isLoading.value = false;
      isErrorTriggered.value = false;
      ticket.reload();
    },
    onError: (error) => {
      if (isErrorTriggered.value) return;
      isErrorTriggered.value = true;

      const text = error.exc_type
        ? (error.messages || error.message || []).join(", ")
        : error.message;
      toast.error(text);

      ticket.reload();
    },
  });
}

function updateOptimistic(fieldname: string, value: string) {
  ticket.data[fieldname] = value;
  toast.success("Ticket updated");
}

onMounted(() => {
  socket.on("helpdesk:ticket-update", (ticketID) => {
    if (ticketID === Number(props.ticketId)) {
      ticket.reload();
    }
  });
});

onUnmounted(() => {
  document.title = "Helpdesk";
  socket.off("helpdesk:ticket-update");
});
</script>

<style>
.breadcrumbs button {
  background-color: inherit !important;

  &:hover,
  &:focus {
    background-color: inherit !important;
  }
}
</style>
