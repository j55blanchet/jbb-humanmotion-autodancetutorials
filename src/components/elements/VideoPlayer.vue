<template>
  <div
    class="video-player-container"
  >
    <video
      :src="videoUrl"
      :style="{
        opacity: '' + videoOpacity,
      }"
      ref="videoElement"
      @loadedmetadata="scheduleCanvasResizing"
      @seeked="onTimeUpdated(true)"
      @timeupdate="onTimeUpdated(true)"
      @ended="endReported = true"
      playsinline
      :controls="showControls"
    ></video>
    <canvas class="is-overlay" ref="canvasElement" v-show="drawPoseLandmarks || motionTrails"></canvas>
  </div>
</template>

<script lang="ts">

import {
  computed,
  defineComponent,
  toRefs,
  onMounted,
  onBeforeUnmount,
  ref,
  nextTick,
  Ref,
  watch,
} from 'vue';
import MotionTrail from '@/model/MotionTrail';
import { DrawPose } from '@/services/MediaPipe';
import { Landmark } from '@/services/MediaPipeTypes';
import poseProvider from '@/services/PoseProvider';

const motionTrailColors = [
  '#59eb59',
  '#6666ff',
];

function onResize(canvasE: HTMLCanvasElement, videoE: HTMLVideoElement, modified: Ref<boolean>) {
  nextTick(() => {
    if (!canvasE || !videoE) return;

    if (canvasE.width !== videoE.offsetWidth) {
      // eslint-disable-next-line no-param-reassign
      canvasE.width = videoE.offsetWidth;
      // eslint-disable-next-line no-param-reassign
      modified.value = true;
    }
    if (canvasE.height !== videoE.offsetHeight) {
      // eslint-disable-next-line no-param-reassign
      canvasE.height = videoE.offsetHeight;
      // eslint-disable-next-line no-param-reassign
      modified.value = true;
    }
    modified.value = true;
  });
}

function setupCanvasResizing(
  videoElement: Ref<null | HTMLVideoElement>,
  canvasElement: Ref<null | HTMLCanvasElement>,
  modified: Ref<boolean>,
) {
  function resizeCanvas() {
    const videoE = videoElement.value;
    const canvasE = canvasElement.value;
    if (videoE && canvasE) onResize(canvasE, videoE, modified);
  }
  onMounted(() => {
    window.addEventListener('resize', resizeCanvas);
    nextTick(resizeCanvas);
  });
  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeCanvas);
  });
  return resizeCanvas;
}

function setupVideoPlaying(
  videoElement: Ref<HTMLVideoElement | null>,
  startTime: Ref<number>,
  endTime: Ref<number>,
  startProgressUpdating: () => void,
  endReported: Ref<boolean>,
) {
  function playVideo(
    from: number,
    to: number,
    speed: number,
  ) {
    // console.log(`VideoPlayer :: Starting playback from ${from} to ${to} @ ${speed.toPrecision(2)}`);

    // eslint-disable-next-line no-param-reassign
    endReported.value = false;
    // eslint-disable-next-line no-param-reassign
    startTime.value = from;
    // eslint-disable-next-line no-param-reassign
    endTime.value = to;

    const videoE = videoElement.value;
    if (!videoE) {
      console.error("VideoE is null - can't start playback");
      return;
    }

    videoE.pause();
    videoE.playbackRate = speed;
    videoE.currentTime = from;

    nextTick(() => {
      startProgressUpdating();
      videoE.play();
    });
  }

  function pauseVideo() {
    const videoE = videoElement.value;
    if (!videoE) {
      console.error("VideoE is null - can't start playback");
      return;
    }
    videoE.pause();
  }

  return { playVideo, pauseVideo };
}

export default defineComponent({
  name: 'VideoPlayer',
  props: {
    videoBaseUrl: {
      type: String,
      required: true,
    },
    motionTrails: {
      type: Array,
      required: false,
    },
    drawMotionTrailsInTime: {
      type: Boolean,
      default: false,
    },
    drawPoseLandmarks: {
      type: Boolean,
      default: false,
    },
    videoOpacity: {
      type: Number,
      default: 1,
    },
    fps: {
      type: Number,
      default: 30,
    },
    setDrawStyle: {
      type: Function,
      default: () => {},
    },
    emphasizedJoints: {
      type: Array,
      default: Array,
    },
    emphasizedJointStyle: {
      type: String,
      default: 'red',
    },
    showControls: {
      type: Boolean,
      default: false,
    },
  },
  emits: [
    'playback-completed',
    'progress',
  ],
  setup(props, ctx) {
    const {
      videoBaseUrl, motionTrails, drawMotionTrailsInTime, drawPoseLandmarks, fps, setDrawStyle, emphasizedJoints, emphasizedJointStyle,
    } = toRefs(props);

    const videoElement = ref(null as null | HTMLVideoElement);
    const canvasElement = ref(null as null | HTMLCanvasElement);
    const canvasCtx = computed(() => canvasElement.value?.getContext('2d') as CanvasRenderingContext2D | null);

    const startTime = ref(0);
    const endTime = ref(0);
    const videoUrl = computed(() => videoBaseUrl?.value ?? '');
    const currentTime = ref(0);
    const canvasModified = ref(false);

    const resizeCanvas = setupCanvasResizing(videoElement, canvasElement, canvasModified);
    const endReported = ref(false);

    const poses = ref([] as Readonly<Array<Readonly<Array<Readonly<Landmark>>>>>);
    const currentFrame = computed(() => Math.floor(currentTime.value * fps.value));
    const currentPose = computed(() => {
      const frame = currentFrame.value;
      const pose = poses.value[frame] ?? [];
      return pose;
    });

    let prevTime = -1;
    let timerId = -1;
    function onTimeUpdated(ignoreEnd?: boolean) {
      const vidElement = videoElement.value;
      if (!vidElement) return;

      const time = vidElement.currentTime;
      if (time === prevTime) return;
      prevTime = time;

      currentTime.value = time;

      if (!ignoreEnd && (time + 1 / 60 >= endTime.value || endReported.value)) {
        vidElement.pause();
        vidElement.currentTime = endTime.value; // pin to end time
        ctx.emit('progress', endTime.value);
        console.log('VideoPlayer :: playback-completed');
        ctx.emit('playback-completed');
        clearInterval(timerId);
        timerId = -1;
      } else {
        ctx.emit('progress', time);
      }
    }

    const startProgressUpdating = () => {
      if (timerId !== -1) clearInterval(timerId);
      timerId = window.setInterval(onTimeUpdated, 1000 / 30);
    };

    const { playVideo, pauseVideo } = setupVideoPlaying(
      videoElement,
      startTime,
      endTime,
      startProgressUpdating,
      endReported,
    );

    function scheduleCanvasResizing() {
      setTimeout(() => {
        nextTick(resizeCanvas);
      }, 100);
    }

    // Update pose drawing
    function clearDrawing() {
      const canvasE = canvasElement.value;
      const drawCtx = canvasCtx.value;
      if (!canvasE || !drawCtx) return;
      drawCtx.clearRect(0, 0, canvasE.width, canvasE.height);
    }
    function drawPose(lms: Landmark[]) {
      const videoE = videoElement.value;
      const sourceAR = (videoE?.videoHeight && videoE.videoHeight) ? videoE.videoWidth / videoE.videoHeight : 1;
      const drawCtx = canvasCtx.value;
      if (!drawCtx) return;
      setDrawStyle.value(drawCtx);
      DrawPose(drawCtx, lms, {
        emphasizedJoints: emphasizedJoints.value as number[],
        emphasisStroke: emphasizedJointStyle.value,
        sourceAspectRatio: sourceAR,
        outlineColor: 'black',
      });
    }

    const retieveClearPoseFile = async () => {
      if (!drawPoseLandmarks.value) {
        poses.value = [];
        return;
      }

      // try {
      poses.value = await poseProvider.GetPose(videoBaseUrl?.value ?? '');
      // } catch (e) {
      // console.error("Couldn't get poses: ", e);
      // }
    };

    function drawArrow(drawCtx: CanvasRenderingContext2D, fromX: number, fromY: number, toX: number, toY: number, atEnd: boolean, arrowLength: number) {

      const arrowWidth = arrowLength / 3;

      const dx = toX - fromX;
      const dy = toY - fromY;
      const angle = Math.atan2(dy, dx);

      drawCtx.save();
      if (atEnd) drawCtx.translate(toX, toY);
      else drawCtx.translate(fromX, fromY);

      drawCtx.rotate(angle);
      drawCtx.lineCap = 'square';
      drawCtx.beginPath();
      drawCtx.ellipse(-arrowLength, 0, arrowLength, arrowWidth, 0, -Math.PI / 2, Math.PI / 2);

      // ctx.lineTo(length - arrow

      drawCtx.stroke();
      drawCtx.restore();
    }

    function drawMotionTrail(trail: Array<[number, number, number]>, time: number, color: string, strokeWidth: number) {
      const videoE = videoElement.value;
      const drawCtx = canvasCtx.value;
      const motionTrailsInTime = drawMotionTrailsInTime.value;
      // console.log('VideoPlayer :: Drawing motion trail', trail);
      const lastTrailItem = trail.findIndex(([t, x, y]) => t >= time);
      // eslint-disable-next-line no-nested-ternary
      const effectiveTrailLength = !motionTrailsInTime ? trail.length
        : (lastTrailItem === -1 ? trail.length : lastTrailItem + 1);

      if (!drawCtx || !videoE) return;
      if (effectiveTrailLength < 2) return;

      drawCtx.save();
      drawCtx.strokeStyle = color;
      drawCtx.globalAlpha = 1.0;
      drawCtx.lineWidth = strokeWidth;

      if (drawCtx.canvas.width <= 0 || drawCtx.canvas.height <= 0) return;
      if (videoE.videoWidth <= 0 || videoE.videoHeight <= 0) return;
      const [xScale, yScale] = [drawCtx.canvas.width / videoE.videoWidth, drawCtx.canvas.height / videoE.videoHeight];
      // console.log('Motion trail scaling', xScale, yScale);
      drawCtx.scale(xScale, yScale);

      drawCtx.beginPath();
      // https://stackoverflow.com/questions/7054272/how-to-draw-smooth-curve-through-n-points-using-javascript-html5-canvas

      const [st, startx, starty] = trail[0];
      drawCtx.moveTo(startx, starty);

      if (effectiveTrailLength <= 2) {
        const [t, x, y] = trail[1];
        drawCtx.lineTo(x, y);
      } else {
        for (let i = 1; i < effectiveTrailLength - 1; i += 1) {
          const [t, x, y] = trail[i];
          const [nt, nx, ny] = trail[i + 1];
          const xc = (x + nx) / 2;
          const yc = (y + ny) / 2;

          if (i === effectiveTrailLength - 2) {
            drawCtx.quadraticCurveTo(x, y, nx, ny);
          } else {
            drawCtx.quadraticCurveTo(x, y, xc, yc);
          }
        }
      }

      drawCtx.stroke();

      const [t2, x2, y2] = trail[1];
      drawArrow(drawCtx, startx, starty, x2, y2, false, 30.0);

      const [lastt, lastx, lasty] = trail[effectiveTrailLength - 1];
      const [secondlastt, secondlastx, secondlasty] = trail[effectiveTrailLength - 2];
      drawArrow(drawCtx, secondlastx, secondlasty, lastx, lasty, true, 30.0);

      // drawCtx.beginPath();

      // drawCtx.moveTo(468.0, 844.8000000000001);
      // drawCtx.lineTo(338.4, 806.4);
      // drawCtx.moveTo(videoE.videoWidth * 0.25, videoE.videoHeight / 2);
      // drawCtx.lineTo(videoE.videoWidth * 0.75, videoE.videoHeight / 2);
      // console.log('videoWH', videoE.videoWidth, videoE.videoHeight);
      // drawCtx.moveTo(0, 0);
      // drawCtx.lineTo(400, 400);
      // drawCtx.stroke();
      drawCtx.restore();
    }

    watch([videoBaseUrl, drawPoseLandmarks], retieveClearPoseFile);
    onMounted(retieveClearPoseFile);

    const motionTrailsCurrentTime = computed(() => {
      const drawingInTime = drawMotionTrailsInTime.value;
      if (!drawingInTime) return 0;
      return currentTime.value;
    });

    watch([canvasModified, currentPose, drawPoseLandmarks, motionTrails, motionTrailsCurrentTime], () => {
      canvasModified.value = false;
      clearDrawing();

      if (drawPoseLandmarks.value) {
        drawPose(currentPose.value as any);
      }

      if (motionTrails && motionTrails.value) {
        for (let i = 0; i < motionTrails.value.length; i += 1) {
          const trail = motionTrails.value[i];
          drawMotionTrail(trail as any, motionTrailsCurrentTime.value, 'black', 9.0);
        }
        for (let i = 0; i < motionTrails.value.length; i += 1) {
          const trail = motionTrails.value[i];
          const color = motionTrailColors[i % motionTrailColors.length];
          drawMotionTrail(trail as any, motionTrailsCurrentTime.value, color, 6.0);
        }
      }
    });

    let resizeTimerId = -1;
    onMounted(() => {
      resizeTimerId = window.setInterval(resizeCanvas, 500);
    });
    onBeforeUnmount(() => {
      clearInterval(resizeTimerId);
    });

    return {
      videoUrl,
      resizeCanvas,
      videoElement,
      canvasElement,
      playVideo,
      pauseVideo,
      endTime,
      scheduleCanvasResizing,
      poses,
      currentTime,
      currentPose,
      currentFrame,
      endReported,
      onTimeUpdated,
      motionTrailsCurrentTime,

      getVideoDimensions: () => ({
        height: videoElement.value?.height ?? 0,
        width: videoElement.value?.width ?? 0,
      }),
    };
  },
  methods: {
    setTime(time: number, keepPlaying?: boolean | undefined) {
      const videoE = this.videoElement;
      if (videoE) {
        videoE.currentTime = time;
      }
      const pauseVideo = !(keepPlaying ?? false);
      if (videoE && pauseVideo) videoE.pause();
    },
    getVideoTime() {
      return this.videoElement?.currentTime ?? 0;
    },
  },
});
</script>

<style lang="scss">
.video-player-container, .canvas-layer {
  position: relative;
  height: 100%;
  display: flex;
  flex-flow: column nowrap;
  justify-content: center;
  align-items: center;

  canvas {
    margin: auto;
    pointer-events: none;
  }

  video {
    flex: 1 1 auto;
    border-radius: 0.25rem;
    display: block;
    margin: auto;
    height: auto;
    max-height: 100%;
  }
}
</style>
