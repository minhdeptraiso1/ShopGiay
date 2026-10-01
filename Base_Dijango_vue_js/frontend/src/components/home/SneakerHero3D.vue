<script setup lang="ts">
import gsap from "gsap";
import { onBeforeUnmount, onMounted, ref } from "vue";

import AppLink from "@/components/navigation/AppLink.vue";
import heroSneakerImg from "@/assets/hero-sneaker.png";

const heroContainerRef = ref<HTMLDivElement | null>(null);
const sneakerWrapRef = ref<HTMLDivElement | null>(null);

const sneakerImgRef = ref<HTMLImageElement | null>(null);
const sneakerImgSrc = heroSneakerImg;

interface Colorway {
  id: string;
  name: string;
  filter: string;
  glow: string;
}

// 3 Phối màu chủ đạo: Xanh Lá (Volt Lime), Cam (Sunset Blaze), Tím (Ultraviolet)
const colorways: Colorway[] = [
  {
    id: "green",
    name: "Volt Lime (Xanh Lá)",
    filter: "none",
    glow: "rgba(163, 230, 53, 0.35)",
  },
  {
    id: "orange",
    name: "Sunset Blaze (Cam)",
    filter: "hue-rotate(300deg) saturate(1.4) brightness(1.05)",
    glow: "rgba(245, 158, 11, 0.35)",
  },
  {
    id: "purple",
    name: "Ultraviolet (Tím)",
    filter: "hue-rotate(185deg) saturate(1.3)",
    glow: "rgba(168, 85, 247, 0.35)",
  },
];

const activeColorway = ref<Colorway>(
  colorways[0] ?? {
    id: "green",
    name: "Volt Lime (Xanh Lá)",
    filter: "none",
    glow: "rgba(163, 230, 53, 0.35)",
  },
);
let currentColorIndex = 0;
let autoColorTimer: ReturnType<typeof globalThis.setInterval> | null = null;

function cycleNextColor() {
  currentColorIndex = (currentColorIndex + 1) % colorways.length;
  const nextColor = colorways[currentColorIndex] ?? activeColorway.value;

  if (!sneakerImgRef.value) {
    activeColorway.value = nextColor;
    return;
  }

  // Hiệu ứng chuyển động mượt mà: phóng to (zoom in) khi đổi màu và tự động trở lại bình thường
  const tl = gsap.timeline();
  tl.to(sneakerImgRef.value, {
    scale: 1.14,
    rotation: -2.5,
    duration: 0.7,
    ease: "power2.out",
    onStart: () => {
      activeColorway.value = nextColor;
    },
  }).to(sneakerImgRef.value, {
    scale: 1,
    rotation: 0,
    duration: 0.9,
    ease: "power2.inOut",
    delay: 0.3,
  });
}

if (typeof globalThis.window !== "undefined") {
  (globalThis.window as unknown as { __cycleHeroColor?: () => void }).__cycleHeroColor =
    cycleNextColor;
}

let gsapCtx: gsap.Context | null = null;
let mouseMoveHandler: ((e: MouseEvent) => void) | null = null;

onMounted(() => {
  const mediaQuery = globalThis.matchMedia("(prefers-reduced-motion: reduce)");
  const prefersReducedMotion = mediaQuery.matches;

  gsapCtx = gsap.context(() => {
    if (prefersReducedMotion) {
      gsap.set([".hero-fade-in", ".hero-spec-tag", sneakerWrapRef.value], { opacity: 1, y: 0 });
      return;
    }

    // Elegant text entrance reveal
    gsap.from(".hero-fade-in", {
      opacity: 0,
      y: 25,
      stagger: 0.1,
      duration: 0.8,
      ease: "power3.out",
    });

    // Sneaker product reveal
    gsap.from(sneakerWrapRef.value, {
      opacity: 0,
      scale: 0.9,
      y: 35,
      duration: 1.1,
      ease: "power3.out",
      delay: 0.2,
    });

    // Tech spec tags pop-in
    gsap.from(".hero-spec-tag", {
      opacity: 0,
      scale: 0.85,
      y: 15,
      stagger: 0.15,
      duration: 0.8,
      ease: "back.out(1.5)",
      delay: 0.6,
    });

    // Gentle floating oscillation
    gsap.to(sneakerWrapRef.value, {
      y: -14,
      duration: 3,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: 1.3,
    });

    // Subtle counter float for spec tags
    gsap.to(".spec-tag-float-1", {
      y: 6,
      duration: 2.4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: 0.2,
    });
    gsap.to(".spec-tag-float-2", {
      y: -8,
      duration: 2.8,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: 0.5,
    });
  }, heroContainerRef.value ?? undefined);

  // Subtle 3D mouse parallax tilt within strict boundaries
  if (!prefersReducedMotion && heroContainerRef.value && sneakerWrapRef.value) {
    mouseMoveHandler = (e: MouseEvent) => {
      if (!heroContainerRef.value || !sneakerWrapRef.value) return;
      const rect = heroContainerRef.value.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;

      gsap.to(sneakerWrapRef.value, {
        rotationY: x * 12,
        rotationX: -y * 8,
        transformPerspective: 1000,
        duration: 0.5,
        ease: "power2.out",
      });
    };

    heroContainerRef.value.addEventListener("mousemove", mouseMoveHandler);
  }

  // Tự động đổi màu giày mỗi 15 giây
  autoColorTimer = globalThis.setInterval(cycleNextColor, 15000);
});

onBeforeUnmount(() => {
  if (autoColorTimer) {
    globalThis.clearInterval(autoColorTimer);
    autoColorTimer = null;
  }
  if (heroContainerRef.value && mouseMoveHandler) {
    heroContainerRef.value.removeEventListener("mousemove", mouseMoveHandler);
  }
  gsapCtx?.revert();
});
</script>

<template>
  <section
    ref="heroContainerRef"
    class="relative isolate w-full overflow-hidden bg-[#090a0f] text-white"
    aria-label="Khu vực giới thiệu sản phẩm Hải Duy Shop"
  >
    <!-- Soft Studio Radial Background Glow (Subtly responds to active sneaker colorway) -->
    <div
      class="pointer-events-none absolute inset-0 opacity-40 transition-all duration-700"
      :style="{
        background: `radial-gradient(circle at 72% 50%, ${activeColorway.glow}, transparent 55%), radial-gradient(circle at 18% 25%, rgba(255, 255, 255, 0.03), transparent 45%)`,
      }"
    />

    <!-- Main 45/55 Hero Grid Container -->
    <div class="relative z-10 mx-auto max-w-7xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
      <div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-12 lg:gap-8">
        <!-- Left Column: Content & CTA (~42% width, lg:col-span-5) -->
        <div class="lg:col-span-5 space-y-6">
          <!-- Eyebrow (No dot, enlarged bold text) -->
          <div
            class="hero-fade-in text-sm sm:text-base font-extrabold tracking-widest text-emerald-400 uppercase"
          >
            HẢI DUY SHOP • PRO SPEED SERIES
          </div>

          <!-- Main Title (Strictly 2 lines, bold, punchy) -->
          <h1
            class="hero-fade-in text-4xl font-black tracking-tight uppercase text-white sm:text-5xl md:text-6xl xl:text-7xl leading-[1.02]"
          >
            BƯỚC PHÁ<br />
            <span class="hero-title-gradient"> GIỚI HẠN. </span>
          </h1>

          <!-- Short 2-line Description -->
          <p class="hero-fade-in max-w-lg text-sm sm:text-base leading-relaxed text-slate-300">
            Thiết kế khí động học cùng công nghệ đệm êm tối tân. Sẵn sàng đồng hành cùng bạn trên
            mọi cung đường và phong cách đường phố tự tin.
          </p>

          <!-- Clear Actions (CTA) -->
          <div class="hero-fade-in flex flex-wrap items-center gap-3 pt-2">
            <AppLink
              to="/#featured-collection"
              class="inline-flex items-center justify-center rounded-full bg-emerald-500 px-7 py-3.5 text-xs font-black tracking-wider text-black uppercase no-underline transition hover:bg-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.4)]"
            >
              Khám phá giày
            </AppLink>
            <AppLink
              to="/#categories"
              class="inline-flex items-center justify-center rounded-full border border-white/20 bg-white/5 px-7 py-3.5 text-xs font-bold tracking-wider text-white uppercase no-underline transition hover:border-white/40 hover:bg-white/10"
            >
              Xem bộ sưu tập
            </AppLink>
          </div>
        </div>

        <!-- Right Column: Sneaker Display Area (~58% width, lg:col-span-7) -->
        <!-- Enlarged sneaker with prominent scale and professional floating tech spec cards -->
        <div class="relative flex flex-col items-center justify-center lg:col-span-7">
          <div
            ref="sneakerWrapRef"
            class="relative w-full max-w-xl lg:max-w-2xl select-none will-change-transform"
          >
            <!-- Spec Card 1: Top Upper (Hyperfuse Mesh) -->
            <div
              class="hero-spec-tag spec-tag-float-1 absolute -top-4 right-6 z-20 hidden sm:flex flex-col gap-1 rounded-2xl border px-4 py-3 shadow-2xl backdrop-blur-md"
            >
              <p class="spec-label spec-emerald text-xs font-bold tracking-wider uppercase">
                Thân Giày Khí Động Học
              </p>
              <p class="spec-value text-sm sm:text-base font-black">
                Hyperfuse Mesh 3 Lớp Thoáng Khí
              </p>
            </div>

            <!-- Spec Card 2: Midsole / Air Cushion (Bottom Left) -->
            <div
              class="hero-spec-tag spec-tag-float-2 absolute -bottom-5 left-2 z-20 hidden sm:flex flex-col gap-1 rounded-2xl border px-4 py-3 shadow-2xl backdrop-blur-md"
            >
              <p class="spec-label spec-sky text-xs font-bold tracking-wider uppercase">
                Hệ Thống Đệm Tối Tân
              </p>
              <p class="spec-value text-sm sm:text-base font-black">Air Max 360 Toàn Bàn Chân</p>
            </div>

            <!-- Spec Card 3: Outsole Grip (Bottom Right) -->
            <div
              class="hero-spec-tag spec-tag-float-3 absolute -bottom-3 right-4 z-20 hidden md:flex flex-col gap-1 rounded-2xl border px-4 py-3 shadow-2xl backdrop-blur-md"
            >
              <p class="spec-label spec-amber text-xs font-bold tracking-wider uppercase">
                Độ Bám Thi Đấu
              </p>
              <p class="spec-value text-sm sm:text-base font-black">Rãnh Xẻ Đa Hướng Bám Sàn</p>
            </div>

            <!-- Authentic Sneaker Product Image with Dynamic Auto Colorway and Zoom Transition -->
            <img
              ref="sneakerImgRef"
              :src="sneakerImgSrc"
              :alt="`Giày thể thao Hải Duy Sneaker - ${activeColorway.name}`"
              loading="eager"
              class="relative z-10 w-full drop-shadow-[0_28px_50px_rgba(0,0,0,0.95)] object-contain transition-[filter] duration-700 will-change-transform"
              :style="{ filter: activeColorway.filter }"
            />

            <!-- Soft Realistic Ground Contact Shadow -->
            <div
              class="mx-auto mt-[-7%] h-9 w-[85%] rounded-[100%] bg-black/80 blur-lg"
              aria-hidden="true"
            />
          </div>

          <!-- Mobile Tech Spec Pills (Visible below sneaker on mobile, no checkmark) -->
          <div class="mt-4 flex flex-wrap items-center justify-center gap-2.5 sm:hidden">
            <span
              class="rounded-full border border-white/15 bg-slate-900/80 px-3.5 py-1.5 text-xs font-bold text-emerald-400 backdrop-blur-md"
            >
              Hyperfuse Mesh 3 Lớp
            </span>
            <span
              class="rounded-full border border-white/15 bg-slate-900/80 px-3.5 py-1.5 text-xs font-bold text-sky-400 backdrop-blur-md"
            >
              Air Max 360
            </span>
            <span
              class="rounded-full border border-white/15 bg-slate-900/80 px-3.5 py-1.5 text-xs font-bold text-amber-400 backdrop-blur-md"
            >
              Đế Bám Đa Hướng
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
