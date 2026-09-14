<template>
  <main class="grid min-h-screen place-items-center px-4 py-10 sm:px-6">
    <section
      class="w-full max-w-md rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-[var(--shadow-surface)] sm:p-8"
    >
      <header class="mb-8">
        <p class="mb-2 text-sm font-semibold tracking-wide text-[var(--color-primary)] uppercase">
          Django Base
        </p>
        <h1 class="text-2xl font-bold tracking-tight text-[var(--color-text)] sm:text-3xl">
          <slot name="title" />
        </h1>
        <p class="mt-2 text-sm text-[var(--color-text-muted)]"><slot name="subtitle" /></p>
      </header>
      <slot />
    </section>
  </main>
</template>
