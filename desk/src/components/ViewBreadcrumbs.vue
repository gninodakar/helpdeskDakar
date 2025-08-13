<template>
  <div class="flex items-center">
    <router-link v-if="routeName" :to="{ name: routeName }"
      class="px-0.5 py-1 text-lg font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-5 hover:text-ink-gray-7 flex items-center justify-center">
      {{ isMobileView ? "..." : safeLabel }}
    </router-link>
    <span v-else class="px-0.5 py-1 text-lg font-medium text-ink-gray-5">
      {{ isMobileView ? "..." : safeLabel }}
    </span>

    <span class="mx-0.5 text-base text-ink-gray-4" aria-hidden="true"> / </span>

    <!-- Render solo si hay opciones y currentView válido -->
    <Dropdown v-if="safeOptions.length" :options="safeOptions">
      <template #default="{ open }">
        <Button variant="ghost" class="text-lg font-medium text-nowrap" :label="safeCurrentView.label">
          <template #prefix>
            <Icon v-if="typeof safeCurrentView.icon === 'string'" :icon="safeCurrentView.icon" class="h-4" />
            <component v-else-if="safeCurrentView.icon" :is="safeCurrentView.icon"
              class="h-4 flex items-center justify-center" />
          </template>
          <template #suffix>
            <FeatherIcon :name="open ? 'chevron-up' : 'chevron-down'" class="h-4 text-ink-gray-8" />
          </template>
        </Button>
      </template>

      <template #item="{ item, active }">
        <button class="group flex text-ink-gray-6 gap-4 h-7 w-full justify-between items-center rounded px-2 text-base"
          :class="{ 'bg-surface-gray-3': active }" @click="item?.onClick?.()">
          <div class="flex items-center">
            <FeatherIcon v-if="item?.icon && typeof item.icon === 'string'" :name="item.icon"
              class="mr-2 h-4 w-4 flex-shrink-0 text-ink-gray-7" aria-hidden="true" />
            <component v-else-if="item?.icon" :is="item.icon" class="mr-2 h-4 w-4 flex-shrink-0 text-ink-gray-7" />
            <span class="whitespace-nowrap">
              {{ item?.label ?? "—" }}
            </span>
          </div>
          <div class="flex flex-row-reverse gap-2 items-center min-w-11">
            <Dropdown v-if="item?.name" :class="active ? 'block' : 'hidden'" placement="right-start"
              :options="dropdownActions(item)">
              <template #default="{ togglePopover }">
                <Button variant="ghost" class="!size-5" icon="more-horizontal" @click.stop="togglePopover()" />
              </template>
            </Dropdown>
            <FeatherIcon v-if="isCurrentView(item)" name="check" class="size-4 text-ink-gray-7" />
          </div>
        </button>
      </template>
    </Dropdown>
  </div>
</template>

<script setup lang="ts">
import Dropdown from "@/components/frappe-ui/Dropdown.vue";
import { useScreenSize } from "@/composables/screen";
import { Icon } from "@iconify/vue";
import { useRoute } from "vue-router";
import { computed } from "vue";

const props = withDefaults(defineProps<{
  routeName?: string;
  label?: string;
  options?: Array<any>;
  dropdownActions: (item: any) => any[];
  currentView?: { label?: string; icon?: any; name?: string } | null;
}>(), {
  label: "—",
  options: () => [],
  currentView: null,
});

const route = useRoute();
const { isMobileView } = useScreenSize();

const safeLabel = computed(() => String(props.label ?? "—"));

const safeOptions = computed(() =>
  (props.options ?? [])
    .filter(Boolean)
    .map((o: any) => ({
      ...o,
      label: String(o?.label ?? o?.title ?? "—"),
    }))
);

const safeCurrentView = computed(() => {
  // Si no viene currentView, intenta deducirlo de options y route.query.view; si no, usa fallback
  const byQuery = safeOptions.value.find(
    (o: any) => o?.name && o.name === route.query.view
  );
  const view = props.currentView || byQuery || safeOptions.value[0] || {};
  return {
    label: String(view?.label ?? "—"),
    icon: view?.icon ?? null,
    name: view?.name ?? null,
  };
});

const isCurrentView = (item: any) => {
  if (!item) return false;
  const q = route.query.view;
  return q ? item.name === q : item.name === safeCurrentView.value.name;
};
</script>
