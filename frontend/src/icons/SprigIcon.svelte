<!-- A sprig: the mark of a rest day. Paths from the dashboard mockup. -->
<script lang="ts"></script>

<svg class="sprig" viewBox="0 0 24 24" aria-hidden="true">
  <path
    d="M11.4 15.3C6.6 15.8 3.3 13 3.3 7.6c5.2-.4 8.2 2.7 8.1 7.7zM12.9 12.8c-.2-5 2.6-8.3 7.9-8.4.1 5.2-2.7 8.5-7.9 8.4zM12.1 17.6c3.1-.4 5.4.9 6.5 3.1-3.1.6-5.4-.5-6.5-3.1z"
    class="leaf"
  />
  <path
    d="M12.2 21.4c-.4-4.4-.6-8.6.1-12.6M5.6 9.8c1.8 1.4 3.6 3 5.4 5.2M18.4 6.6c-1.6 1.6-3.4 3.6-5.2 5.8"
    class="vein"
  />
</svg>

<style>
  .sprig {
    width: var(--size-icon);
    height: var(--size-icon);
  }

  .leaf {
    fill: var(--growth-text);
    stroke: var(--icon-line);
    stroke-width: 1.1;
    stroke-linejoin: round;
  }

  .vein {
    fill: none;
    stroke: var(--icon-line);
    stroke-width: 1.3;
    stroke-linecap: round;
  }
</style>
