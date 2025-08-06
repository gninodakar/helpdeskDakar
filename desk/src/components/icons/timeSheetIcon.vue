<template>
  <!-- Minimal Clock Icon (16×16) -->
  <svg
    width="24"
    height="24"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <!-- Clock face -->
    <circle
      cx="8"
      cy="8"
      r="5"
      fill="#fff"
      stroke="#0a0a0a"
      stroke-width="0.8"
    />

    <!-- Hour hand (shorter line) -->
    <line
      x1="8"
      y1="8"
      x2="8"
      y2="5.5"
      stroke="#0a0a0a"
      stroke-width="0.8"
      stroke-linecap="round"
    />

    <!-- Minute hand (longer line) -->
    <line
      x1="8"
      y1="8"
      x2="11"
      y2="8"
      stroke="#0a0a0a"
      stroke-width="0.8"
      stroke-linecap="round"
    />
  </svg>
</template>
