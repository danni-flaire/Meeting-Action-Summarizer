<script setup>
import { ref, computed } from "vue";
import {
  ArrowRight,
  Terminal,
  Check,
  Copy,
  Loader2,
  AlertCircle,
  FileText,
  CornerDownLeft,
} from "lucide-vue-next";

// Endpoint definition
const ENDPOINT_URL = "https://meeting-action-summarizer-app.vercel.app/extract";

// Sample meeting transcripts for quick testing and demonstration
const SAMPLE_TRANSCRIPTS = {
  sprint: `Team Sync Transcript -- Nov 18, 2024
Participants: Sarah (Tech Lead), Alex (Frontend), David (Backend), Elena (Product Manager)

Elena: Let's review where we stand on the Q4 release milestones. We need to lock down the auth migration and ensure the new latency SLAs are met before December 1st.
David: On the backend side, PostgreSQL connection pooling with PgBouncer is configured on staging. However, we discovered a connection exhaustion issue during the load test yesterday at 4,000 req/sec. I will patch the maximum client pool limit and run a complete benchmark by this Thursday.
Sarah: Agreed. We cannot ship this without seeing at least 5,000 req/sec sustained with sub-50ms p95 latency. That is a hard requirement. We officially decided to delay the customer migration until that benchmark passes.
Alex: On the frontend, we finished integrating the new session token refresh flow. But we still need to handle graceful session expiry modals. I will complete the modal component and add unit test coverage for token expiry edge cases by Friday afternoon.
Elena: Perfect. What about the SOC2 compliance checklist?
Sarah: We decided to use AWS KMS for encrypting all database backups at rest instead of managing our own keys. I will draft the KMS architecture documentation and update our Terraform templates by next Monday.
Elena: Great. I will schedule the final security review meeting with legal for next Wednesday once Sarah's Terraform PR is merged. Let's reconvene on Thursday morning for a quick check-in.`,

  incident: `Post-Mortem Transcript -- Incident #408 API Gateway Outage
Participants: Marcus (VP Infra), Chloe (SRE Lead), Ryan (Core Services)

Marcus: Starting the post-mortem for the 14-minute outage on the EU-Central API Gateway yesterday.
Chloe: The root cause was an unthrottled cache eviction storm triggered during the canary deployment of build v2.14. Redis CPU hit 100%, causing health checks to fail and the load balancer to deregister all gateway targets.
Ryan: We made the immediate operational decision during the incident to revert back to build v2.13 and add a fallback in-memory cache circuit breaker.
Marcus: Good call. We need systematic fixes so this never reoccurs. First decision: all future cache eviction scripts must enforce a rate limit of maximum 500 keys per second.
Chloe: I will implement the eviction rate-limiter in the Redis client wrapper by Wednesday, 5 PM.
Ryan: I will add synthetic canary health checks that evaluate Redis CPU saturation before traffic switching by Friday, Nov 22.
Marcus: I will draft the formal post-mortem report and publish it to the customer trust portal by Monday morning.`,
};

// Reactive state
const transcript = ref("");
const isLoading = ref(false);
const errorMessage = ref("");
const extractedData = ref(null);
const copySuccess = ref(false);
const endpointStatus = ref("READY"); // 'READY' | 'ACTIVE' | 'ERROR'

// Computed metrics
const charCount = computed(() => transcript.value.length);
const wordCount = computed(() => {
  const trimmed = transcript.value.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
});

// Methods
function loadSample(key = "sprint") {
  transcript.value = SAMPLE_TRANSCRIPTS[key] || SAMPLE_TRANSCRIPTS.sprint;
  errorMessage.value = "";
  scrollToWorkspace();
}

function clearAll() {
  transcript.value = "";
  extractedData.value = null;
  errorMessage.value = "";
  copySuccess.value = false;
  endpointStatus.value = "READY";
}

function scrollToWorkspace() {
  const el = document.getElementById("workspace");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  }
}

async function extractActionItems() {
  if (!transcript.value.trim()) {
    errorMessage.value =
      "Please provide a meeting transcript before initiating extraction.";
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";
  endpointStatus.value = "ACTIVE";

  try {
    const response = await fetch(ENDPOINT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        transcript: transcript.value,
      }),
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          detail =
            typeof errorJson.detail === "string"
              ? errorJson.detail
              : JSON.stringify(errorJson.detail);
        }
      } catch {
        // use fallback status text
      }
      throw new Error(`Extraction failed: ${detail}`);
    }

    const data = await response.json();

    // Validate required fields
    if (!data || typeof data.meeting_summary !== "string") {
      throw new Error("Invalid response structure: missing meeting_summary.");
    }

    extractedData.value = {
      meeting_summary: data.meeting_summary || "",
      key_decisions: Array.isArray(data.key_decisions)
        ? data.key_decisions
        : [],
      action_items: Array.isArray(data.action_items) ? data.action_items : [],
    };
    endpointStatus.value = "READY";
  } catch (err) {
    endpointStatus.value = "ERROR";
    if (
      err instanceof TypeError &&
      err.message.toLowerCase().includes("fetch")
    ) {
      errorMessage.value = `Unable to connect to backend at ${ENDPOINT_URL}. Ensure the service is reachable with CORS enabled.`;
    } else {
      errorMessage.value =
        err.message ||
        "An unexpected error occurred during transcript processing.";
    }
  } finally {
    isLoading.value = false;
  }
}

async function copyAsJson() {
  if (!extractedData.value) return;
  try {
    const formatted = JSON.stringify(extractedData.value, null, 2);
    await navigator.clipboard.writeText(formatted);
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  } catch {
    // Clipboard API fallback
    const textarea = document.createElement("textarea");
    textarea.value = JSON.stringify(extractedData.value, null, 2);
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-white text-[#0A0A0A] font-sans antialiased selection:bg-black selection:text-white"
  >
    <!-- 1. Top Navigation Bar -->
    <header
      class="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-neutral-200"
    >
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between"
      >
        <!-- Brand Mark -->
        <a href="#" class="flex items-center gap-2 group">
          <span
            class="font-mono text-xs font-semibold tracking-wider text-black uppercase"
          >
            EXTRACT // 01
          </span>
          <span class="hidden sm:inline-block w-1.5 h-1.5 bg-black"></span>
          <span
            class="hidden sm:inline-block font-mono text-[11px] text-neutral-500 uppercase tracking-tight"
          >
            Meeting Action Item Extractor
          </span>
        </a>

        <!-- Navigation Links & Action Button -->
        <nav class="flex items-center gap-4 sm:gap-6">
          <a
            href="#architecture"
            class="text-xs font-mono uppercase tracking-wider text-neutral-600 hover:text-black transition-colors"
          >
            Architecture
          </a>
          <a
            href="#api-spec"
            class="text-xs font-mono uppercase tracking-wider text-neutral-600 hover:text-black transition-colors"
          >
            API Spec
          </a>
          <button
            type="button"
            @click="scrollToWorkspace"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-black text-white hover:bg-neutral-800 text-xs font-mono uppercase tracking-wider rounded-none transition-colors border border-black"
          >
            <span>Launch Workspace</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </button>
        </nav>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 2. Hero Section -->
      <section
        class="pt-16 pb-14 sm:pt-24 sm:pb-20 border-b border-neutral-200"
      >
        <div class="max-w-4xl">
          <!-- Eyebrow label -->
          <div
            class="inline-flex items-center gap-2 px-2 py-1 mb-6 border border-neutral-200 bg-[#FAFAFA]"
          >
            <Terminal class="w-3.5 h-3.5 text-black" />
            <span
              class="font-mono text-[11px] uppercase tracking-wider text-black font-medium"
            >
              FASTAPI + PYDANTIC + QWEN 2.5 32B (qwen/qwen3.8-27b)
            </span>
          </div>

          <!-- Headline -->
          <h1
            class="text-4xl sm:text-6xl lg:text-7xl font-semibold tracking-tight text-[#0A0A0A] leading-[1.05] mb-6"
          >
            Turn unstructured meeting transcripts into deterministic JSON.
          </h1>

          <!-- Subheadline -->
          <p
            class="text-base sm:text-lg text-[#52525B] leading-relaxed max-w-2xl mb-8"
          >
            Raw meeting transcripts stream into our pipeline and emerge as
            strictly validated summaries, decisive alignments, and assigned
            action items. Powered by Groq's high-throughput Qwen (qwen/qwen3.8-27b) inference
            engine with deterministic Pydantic v2 schema enforcement.
          </p>

          <!-- Action row -->
          <div class="flex flex-wrap items-center gap-3">
            <button
              type="button"
              @click="scrollToWorkspace"
              class="inline-flex items-center gap-2 px-5 py-2.5 bg-black text-white hover:bg-neutral-800 text-xs font-mono uppercase tracking-wider rounded-none transition-colors border border-black"
            >
              <span>Try Live Demo</span>
              <CornerDownLeft class="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              @click="loadSample('sprint')"
              class="inline-flex items-center gap-2 px-5 py-2.5 bg-[#FAFAFA] text-black hover:bg-neutral-100 text-xs font-mono uppercase tracking-wider rounded-none transition-colors border border-neutral-200"
            >
              <FileText class="w-3.5 h-3.5 text-neutral-600" />
              <span>Load Sample Transcript</span>
            </button>
          </div>
        </div>
      </section>

      <!-- 3. Interactive Workspace -->
      <section id="workspace" class="py-12 sm:py-16 scroll-mt-14">
        <!-- Section Header -->
        <div
          class="mb-4 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2"
        >
          <div>
            <div
              class="font-mono text-xs text-neutral-500 uppercase tracking-wider"
            >
              Workspace // Execution Environment
            </div>
            <h2
              class="text-xl sm:text-2xl font-semibold tracking-tight text-[#0A0A0A]"
            >
              Interactive Extraction Workspace
            </h2>
          </div>
          <div
            class="flex items-center gap-2 text-xs font-mono text-neutral-500"
          >
            <span>Status:</span>
            <span
              :class="[
                'inline-flex items-center gap-1.5 px-2 py-0.5 border font-mono text-[11px] uppercase tracking-wider',
                endpointStatus === 'READY'
                  ? 'border-neutral-300 bg-[#FAFAFA] text-neutral-800'
                  : '',
                endpointStatus === 'ACTIVE'
                  ? 'border-black bg-black text-white'
                  : '',
                endpointStatus === 'ERROR'
                  ? 'border-neutral-400 bg-neutral-100 text-black'
                  : '',
              ]"
            >
              <span
                :class="[
                  'w-1.5 h-1.5',
                  endpointStatus === 'READY' ? 'bg-neutral-400' : '',
                  endpointStatus === 'ACTIVE' ? 'bg-white animate-pulse' : '',
                  endpointStatus === 'ERROR' ? 'bg-black' : '',
                ]"
              ></span>
              {{ endpointStatus }}
            </span>
          </div>
        </div>

        <!-- Crisp full-width 1px black-bordered container -->
        <div class="border border-black bg-white">
          <!-- Top bar inside container -->
          <div
            class="px-4 py-2.5 bg-[#FAFAFA] border-b border-black flex flex-wrap items-center justify-between gap-2"
          >
            <div class="flex items-center gap-2">
              <span class="inline-block w-2 h-2 bg-black"></span>
              <span class="font-mono text-xs font-medium text-black">
                POST {{ ENDPOINT_URL }}
              </span>
              <span
                class="hidden md:inline font-mono text-[11px] text-neutral-500"
              >
                (Content-Type: application/json)
              </span>
            </div>

            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="loadSample('sprint')"
                class="px-2.5 py-1 text-xs font-mono uppercase tracking-wider text-neutral-700 hover:text-black hover:bg-neutral-200 border border-neutral-300 bg-white rounded-none transition-colors"
              >
                Sample 1
              </button>
              <button
                type="button"
                @click="loadSample('incident')"
                class="px-2.5 py-1 text-xs font-mono uppercase tracking-wider text-neutral-700 hover:text-black hover:bg-neutral-200 border border-neutral-300 bg-white rounded-none transition-colors"
              >
                Sample 2
              </button>
              <button
                type="button"
                @click="clearAll"
                class="px-2.5 py-1 text-xs font-mono uppercase tracking-wider text-neutral-700 hover:text-black hover:bg-neutral-200 border border-neutral-300 bg-white rounded-none transition-colors"
              >
                Clear
              </button>
            </div>
          </div>

          <!-- Two-column split (50% / 50% on desktop, separated by 1px vertical divider) -->
          <div
            class="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-neutral-200 min-h-[580px]"
          >
            <!-- Left Pane (Input) -->
            <div class="flex flex-col bg-white">
              <div
                class="px-4 py-2 bg-white border-b border-neutral-200 flex items-center justify-between"
              >
                <span
                  class="font-mono text-xs uppercase tracking-wider text-neutral-500"
                >
                  Input Transcript
                </span>
                <span class="font-mono text-[11px] text-neutral-400">
                  Raw Text
                </span>
              </div>

              <!-- Full-height borderless textarea -->
              <textarea
                v-model="transcript"
                placeholder="Paste meeting transcript, notes, or dialogue here..."
                class="flex-1 w-full p-4 font-mono text-xs sm:text-sm text-[#0A0A0A] placeholder-neutral-400 bg-white border-0 resize-none focus:outline-none focus:ring-0 leading-relaxed min-h-[380px]"
                spellcheck="false"
              ></textarea>

              <!-- Bottom toolbar -->
              <div
                class="px-4 py-3 bg-[#FAFAFA] border-t border-neutral-200 flex flex-wrap items-center justify-between gap-3"
              >
                <div
                  class="flex items-center gap-4 font-mono text-xs text-[#52525B]"
                >
                  <span
                    >Chars:
                    <strong class="text-black font-semibold">{{
                      charCount
                    }}</strong></span
                  >
                  <span class="text-neutral-300">/</span>
                  <span
                    >Words:
                    <strong class="text-black font-semibold">{{
                      wordCount
                    }}</strong></span
                  >
                </div>

                <button
                  type="button"
                  @click="extractActionItems"
                  :disabled="isLoading || !transcript.trim()"
                  class="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-black text-white hover:bg-neutral-800 disabled:bg-neutral-200 disabled:text-neutral-500 disabled:cursor-not-allowed text-xs font-mono uppercase tracking-wider rounded-none transition-colors border border-black disabled:border-neutral-200 cursor-pointer"
                >
                  <Loader2 v-if="isLoading" class="w-3.5 h-3.5 animate-spin" />
                  <ArrowRight v-else class="w-3.5 h-3.5" />
                  <span>{{
                    isLoading ? "Extracting..." : "Extract Action Items"
                  }}</span>
                </button>
              </div>
            </div>

            <!-- Right Pane (Structured Output) -->
            <div class="flex flex-col bg-white">
              <div
                class="px-4 py-2 bg-white border-b border-neutral-200 flex items-center justify-between"
              >
                <span
                  class="font-mono text-xs uppercase tracking-wider text-neutral-500"
                >
                  Structured Output
                </span>
                <span class="font-mono text-[11px] text-neutral-400">
                  Pydantic v2 Validated
                </span>
              </div>

              <!-- Content Area with States -->
              <div class="flex-1 flex flex-col min-h-[420px] bg-white">
                <!-- Loading State -->
                <div
                  v-if="isLoading"
                  class="flex-1 flex flex-col items-center justify-center p-8 text-center"
                >
                  <Loader2 class="w-6 h-6 animate-spin text-black mb-3" />
                  <div
                    class="font-mono text-xs text-black uppercase tracking-wider"
                  >
                    Parsing transcript via Groq...
                  </div>
                  <div class="font-mono text-[11px] text-[#52525B] mt-1">
                    Enforcing schema: MeetingOutput
                  </div>
                </div>

                <!-- Error State -->
                <div
                  v-else-if="errorMessage"
                  class="p-6 m-4 border border-black bg-[#FAFAFA]"
                >
                  <div class="flex items-start gap-3">
                    <AlertCircle class="w-5 h-5 text-black shrink-0 mt-0.5" />
                    <div class="flex-1">
                      <div
                        class="font-mono text-xs uppercase tracking-wider font-semibold text-black mb-1"
                      >
                        Extraction Failure
                      </div>
                      <p
                        class="font-mono text-xs text-[#52525B] leading-relaxed break-words"
                      >
                        {{ errorMessage }}
                      </p>
                      <div
                        class="mt-4 pt-3 border-t border-neutral-200 flex items-center justify-between"
                      >
                        <span class="font-mono text-[11px] text-neutral-400">
                          Verify FastAPI endpoint is reachable
                        </span>
                        <button
                          type="button"
                          @click="extractActionItems"
                          class="font-mono text-xs uppercase tracking-wider text-black underline underline-offset-2 hover:no-underline"
                        >
                          Retry Request
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Empty State -->
                <div
                  v-else-if="!extractedData"
                  class="flex-1 flex flex-col items-center justify-center p-8 text-center"
                >
                  <div
                    class="w-10 h-10 border border-neutral-200 flex items-center justify-center mb-3 bg-[#FAFAFA]"
                  >
                    <Terminal class="w-4 h-4 text-neutral-400" />
                  </div>
                  <div
                    class="font-mono text-xs uppercase tracking-wider text-neutral-500"
                  >
                    Awaiting transcript input...
                  </div>
                  <div
                    class="font-mono text-[11px] text-neutral-400 mt-1 max-w-xs"
                  >
                    Paste raw text on the left pane or click "Sample" above to
                    populate realistic notes.
                  </div>
                </div>

                <!-- Populated State -->
                <div v-else class="flex-1 flex flex-col">
                  <!-- Output Top Bar with Copy JSON button -->
                  <div
                    class="px-4 py-2.5 bg-[#FAFAFA] border-b border-neutral-200 flex items-center justify-between"
                  >
                    <div class="flex items-center gap-2">
                      <span class="w-1.5 h-1.5 bg-black"></span>
                      <span
                        class="font-mono text-xs uppercase tracking-wider text-black font-medium"
                      >
                        Schema Validation Passed
                      </span>
                    </div>

                    <button
                      type="button"
                      @click="copyAsJson"
                      class="inline-flex items-center gap-1.5 px-3 py-1 border border-black bg-white hover:bg-black hover:text-white text-xs font-mono uppercase tracking-wider rounded-none transition-colors"
                    >
                      <Check
                        v-if="copySuccess"
                        class="w-3.5 h-3.5 text-black hover:text-white"
                      />
                      <Copy v-else class="w-3.5 h-3.5" />
                      <span>{{ copySuccess ? "Copied" : "Copy JSON" }}</span>
                    </button>
                  </div>

                  <!-- Editorial Blocks -->
                  <div class="flex-1 divide-y divide-neutral-200">
                    <!-- 1) SUMMARY -->
                    <div class="p-6">
                      <div
                        class="font-mono text-xs uppercase tracking-wider text-neutral-500 mb-2"
                      >
                        01 // Summary
                      </div>
                      <p
                        class="text-sm sm:text-base text-[#0A0A0A] leading-relaxed"
                      >
                        {{ extractedData.meeting_summary }}
                      </p>
                    </div>

                    <!-- 2) KEY DECISIONS -->
                    <div class="p-6">
                      <div
                        class="font-mono text-xs uppercase tracking-wider text-neutral-500 mb-3"
                      >
                        02 // Key Decisions
                      </div>
                      <ul
                        v-if="
                          extractedData.key_decisions &&
                          extractedData.key_decisions.length
                        "
                        class="space-y-2.5"
                      >
                        <li
                          v-for="(decision, idx) in extractedData.key_decisions"
                          :key="idx"
                          class="flex items-start gap-3 text-xs sm:text-sm text-[#0A0A0A] leading-relaxed"
                        >
                          <span
                            class="w-1.5 h-1.5 bg-black mt-2 shrink-0"
                          ></span>
                          <span class="flex-1">{{ decision }}</span>
                        </li>
                      </ul>
                      <p
                        v-else
                        class="font-mono text-xs text-neutral-400 italic"
                      >
                        No key decisions identified in this transcript.
                      </p>
                    </div>

                    <!-- 3) ACTION ITEMS -->
                    <div class="p-6">
                      <div
                        class="font-mono text-xs uppercase tracking-wider text-neutral-500 mb-3 flex items-center justify-between"
                      >
                        <span>03 // Action Items</span>
                        <span class="text-neutral-400">
                          Count:
                          {{
                            extractedData.action_items
                              ? extractedData.action_items.length
                              : 0
                          }}
                        </span>
                      </div>

                      <div
                        v-if="
                          extractedData.action_items &&
                          extractedData.action_items.length
                        "
                        class="border border-neutral-200 overflow-x-auto"
                      >
                        <table class="w-full text-left border-collapse">
                          <thead>
                            <tr
                              class="bg-[#FAFAFA] border-b border-neutral-200 font-mono text-[11px] uppercase tracking-wider text-neutral-600"
                            >
                              <th class="py-2.5 px-3 font-medium">Task</th>
                              <th class="py-2.5 px-3 font-medium w-32">
                                Owner
                              </th>
                              <th class="py-2.5 px-3 font-medium w-36">
                                Deadline
                              </th>
                            </tr>
                          </thead>
                          <tbody
                            class="divide-y divide-neutral-200 text-xs sm:text-sm"
                          >
                            <tr
                              v-for="(item, idx) in extractedData.action_items"
                              :key="idx"
                              class="hover:bg-[#FAFAFA] transition-colors"
                            >
                              <td
                                class="py-2.5 px-3 text-[#0A0A0A] leading-normal font-normal"
                              >
                                {{ item.task }}
                              </td>
                              <td class="py-2.5 px-3 whitespace-nowrap">
                                <span
                                  class="inline-block px-2 py-0.5 border border-neutral-300 font-mono text-[11px] text-black bg-[#FAFAFA] rounded-none"
                                >
                                  {{ item.owner || "Unassigned" }}
                                </span>
                              </td>
                              <td
                                class="py-2.5 px-3 font-mono text-xs text-[#52525B] whitespace-nowrap"
                              >
                                {{ item.deadline || "TBD" }}
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <p
                        v-else
                        class="font-mono text-xs text-neutral-400 italic"
                      >
                        No action items were extracted from this transcript.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 4. Technical Specification Section -->
      <section
        id="architecture"
        class="py-12 sm:py-16 border-t border-neutral-200"
      >
        <div class="mb-8">
          <div
            class="font-mono text-xs text-neutral-500 uppercase tracking-wider"
          >
            Architecture // System Design
          </div>
          <h2
            class="text-2xl sm:text-3xl font-semibold tracking-tight text-[#0A0A0A] mt-1"
          >
            Technical Specification
          </h2>
          <p class="text-sm sm:text-base text-[#52525B] mt-2 max-w-2xl">
            A production-grade pipeline structured around strict schema
            validation and ultra-fast Groq hardware acceleration.
          </p>
        </div>

        <!-- 2-column key-value specification table styled like Vercel/Notion technical documentation -->
        <div class="border-t border-neutral-200">
          <dl class="divide-y divide-neutral-200 text-sm">
            <div
              class="py-4 grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4 items-baseline"
            >
              <dt
                class="font-mono text-xs uppercase tracking-wider text-black font-semibold"
              >
                Inference Engine
              </dt>
              <dd class="sm:col-span-2 text-[#0A0A0A]">
                Qwen (qwen/qwen3.8-27b) via Groq API
                <span class="block font-mono text-xs text-[#52525B] mt-0.5">
                  Operates in Strict JSON Mode (`response_format: {"type":
                  "json_object"}`) on Groq LPUs.
                </span>
              </dd>
            </div>

            <div
              class="py-4 grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4 items-baseline"
            >
              <dt
                class="font-mono text-xs uppercase tracking-wider text-black font-semibold"
              >
                Validation Layer
              </dt>
              <dd class="sm:col-span-2 text-[#0A0A0A]">
                Pydantic v2 Schema Enforcement
                <span class="block font-mono text-xs text-[#52525B] mt-0.5">
                  Strict typing via
                  <code
                    class="px-1 py-0.5 bg-[#FAFAFA] border border-neutral-200 text-black"
                    >MeetingInput</code
                  >
                  and
                  <code
                    class="px-1 py-0.5 bg-[#FAFAFA] border border-neutral-200 text-black"
                    >MeetingOutput</code
                  >
                  data contracts.
                </span>
              </dd>
            </div>

            <div
              class="py-4 grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4 items-baseline"
            >
              <dt
                class="font-mono text-xs uppercase tracking-wider text-black font-semibold"
              >
                Backend Framework
              </dt>
              <dd class="sm:col-span-2 text-[#0A0A0A]">
                FastAPI asynchronous REST endpoint
                <span class="block font-mono text-xs text-[#52525B] mt-0.5">
                  High-concurrency ASGI pipeline running on Uvicorn with
                  auto-generated OpenAPI documentation.
                </span>
              </dd>
            </div>

            <div
              class="py-4 grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4 items-baseline"
            >
              <dt
                class="font-mono text-xs uppercase tracking-wider text-black font-semibold"
              >
                Latency Target
              </dt>
              <dd class="sm:col-span-2 text-[#0A0A0A]">
                Sub-second extraction for standard 1,500-word transcripts
                <span class="block font-mono text-xs text-[#52525B] mt-0.5">
                  Engineered for real-time executive summaries with zero queuing
                  overhead.
                </span>
              </dd>
            </div>

            <div
              class="py-4 grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4 items-baseline"
            >
              <dt
                class="font-mono text-xs uppercase tracking-wider text-black font-semibold"
              >
                Client Architecture
              </dt>
              <dd class="sm:col-span-2 text-[#0A0A0A]">
                Vue 3 Composition API + Tailwind CSS
                <span class="block font-mono text-xs text-[#52525B] mt-0.5">
                  Zero external UI component bloat. Clean reactive state
                  management and native Fetch API streaming.
                </span>
              </dd>
            </div>
          </dl>
        </div>

        <!-- API Spec Detail Block -->
        <div
          id="api-spec"
          class="mt-12 pt-8 border-t border-neutral-200 scroll-mt-14"
        >
          <div
            class="font-mono text-xs text-neutral-500 uppercase tracking-wider mb-2"
          >
            Contract // REST API Specification
          </div>
          <h3 class="text-lg font-semibold tracking-tight text-[#0A0A0A] mb-4">
            Endpoint Contract: POST /extract
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Request Schema -->
            <div class="border border-neutral-200 bg-[#FAFAFA] p-4">
              <div class="flex items-center justify-between mb-2">
                <span
                  class="font-mono text-xs font-semibold uppercase tracking-wider text-black"
                >
                  Request Payload (JSON)
                </span>
                <span class="font-mono text-[11px] text-neutral-500">
                  MeetingInput
                </span>
              </div>
              <pre
                class="font-mono text-xs text-[#0A0A0A] overflow-x-auto p-3 bg-white border border-neutral-200"
              ><code>{
  "transcript": "string (raw dialogue or meeting notes)"
}</code></pre>
            </div>

            <!-- Response Schema -->
            <div class="border border-neutral-200 bg-[#FAFAFA] p-4">
              <div class="flex items-center justify-between mb-2">
                <span
                  class="font-mono text-xs font-semibold uppercase tracking-wider text-black"
                >
                  Response Model (JSON)
                </span>
                <span class="font-mono text-[11px] text-neutral-500">
                  MeetingOutput
                </span>
              </div>
              <pre
                class="font-mono text-xs text-[#0A0A0A] overflow-x-auto p-3 bg-white border border-neutral-200"
              ><code>{
  "meeting_summary": "string",
  "key_decisions": [
    "string"
  ],
  "action_items": [
    {
      "task": "string",
      "owner": "string",
      "deadline": "string"
    }
  ]
}</code></pre>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 5. Footer -->
    <footer class="border-t border-neutral-200 bg-white mt-16">
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row items-center justify-between gap-4"
      >
        <div class="font-mono text-xs text-[#52525B]">
          <span>EXTRACT // 01</span>
          <span class="mx-2 text-neutral-300">/</span>
          <span>FastAPI + Pydantic v2 + Qwen (qwen/qwen3.8-27b)</span>
          <span class="mx-2 text-neutral-300">/</span>
          <span>Deterministic JSON Extraction Pipeline</span>
        </div>

        <div class="flex items-center gap-4">
          <a
            href="https://github.com/danni-flaire/Meeting-Action-Summarizer"
            target="_blank"
            rel="noopener noreferrer"
            class="font-mono text-xs uppercase tracking-wider text-neutral-600 hover:text-black transition-colors"
          >
            GitHub Repository
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>
