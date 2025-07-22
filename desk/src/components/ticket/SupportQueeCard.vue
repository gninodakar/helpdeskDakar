<template>
  <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
    <div class="flex justify-between items-start mb-2">
      <div>
        <h3 class="text-lg font-semibold text-gray-900">{{ queue.name }}</h3>
        <p class="text-gray-500 text-sm">{{ queue.email }}</p>
      </div>
      <div class="text-gray-400">
        <LucideMoreVertical class="h-5 w-5" />
      </div>
    </div>

    <div class="flex items-center justify-between mb-4">
      <Button label="Tickets" theme="gray" variant="solid" class="mr-2 px-3 py-1.5 text-sm">
        <template #prefix>
          <LucideTicket class="h-4 w-4" />
        </template>
      </Button>
      <span class="text-gray-600 text-sm">Tickets Closed: {{ queue.ticketsClosed }}</span>
      <span v-if="queue.slaSuccessRate !== undefined"
            class="ml-auto font-medium text-sm"
            :class="getSlaColor(queue.slaSuccessRate)">
        SLA Success Rate: {{ queue.slaSuccessRate }}%
      </span>
    </div>

    <div class="grid grid-cols-4 text-center text-sm font-medium border-t pt-4 mt-4">
      <div>
        <p class="text-blue-600 text-lg font-bold">{{ queue.open }}</p>
        <p class="text-gray-500">Open</p>
      </div>
      <div>
        <p class="text-blue-600 text-lg font-bold">{{ queue.unassigned }}</p>
        <p class="text-gray-500">Unassigned</p>
      </div>
      <div>
        <p class="text-blue-600 text-lg font-bold">{{ queue.urgent }}</p>
        <p class="text-gray-500">Urgent</p>
      </div>
      <div>
        <p class="text-blue-600 text-lg font-bold">{{ queue.failed }}</p>
        <p class="text-gray-500">Failed</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import Button from '@/components/Button.vue'; 
import LucideMoreVertical from '~icons/lucide/more-vertical'; 
import LucideTicket from '~icons/lucide/ticket'; 
interface SupportQueue {
  name: string;
  email: string;
  ticketsClosed: number;
  slaSuccessRate?: number;
  open: number;
  unassigned: number;
  urgent: number;
  failed: number;
}

const props = defineProps<{
  queue: SupportQueue;
}>();

const getSlaColor = (rate: number) => {
  if (rate >= 90) return 'text-green-600';
  if (rate >= 70) return 'text-orange-600';
  return 'text-red-600';
};
</script>