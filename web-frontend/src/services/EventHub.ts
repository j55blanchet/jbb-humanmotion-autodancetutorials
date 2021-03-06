import { TinyEmitter } from 'tiny-emitter';
import { onMounted, onBeforeUnmount } from 'vue';
import { MpHolisticResults } from './MediaPipeTypes';

export const EventNames = Object.freeze({
  gesture: 'gesture',
  trackingProcessingStarted: 'trackingProcessingStarted',
  trackingResults: 'trackingResults',
  trackingRequested: 'trackingRequested',
  trackingRequestFinished: 'trackingRequestFinished',
});

export const GestureNames = Object.freeze({
  none: 'none',
  pointLeft: 'point-left',
  pointRight: 'point-right',
  namaste: 'namaste',
});

const eventHub = new TinyEmitter();

export function setupGestureListening(
  callbacks: Record<string, (trackingResults?: MpHolisticResults | undefined) => void>,
  fallback?: undefined | ((gesture: string, trackingResults: MpHolisticResults) => void),
) {
  function onGesture(gesture: string, trackingResults: MpHolisticResults) {
    const cb = callbacks[gesture];
    if (cb) cb(trackingResults);

    if (!cb && fallback) fallback(gesture, trackingResults);
  }
  onMounted(() => {
    eventHub.on(EventNames.gesture, onGesture);
  });
  onBeforeUnmount(() => {
    eventHub.off(EventNames.gesture, onGesture);
  });
}

export function setupMediaPipeListening(
  callback: (res: MpHolisticResults, frameId?: number) => void,
  onFrameProcessingStarted?: (frameId: number) => void,
) {

  onMounted(() => {
    eventHub.on(EventNames.trackingResults, callback);
    if (onFrameProcessingStarted) eventHub.on(EventNames.trackingProcessingStarted, onFrameProcessingStarted);
  });
  onBeforeUnmount(() => {
    eventHub.off(EventNames.trackingResults, callback);
    if (onFrameProcessingStarted) eventHub.off(EventNames.trackingProcessingStarted, onFrameProcessingStarted);
  });
}

export const TrackingActions = Object.freeze({
  requestTracking: (id: string) => {
    eventHub.emit(EventNames.trackingRequested, id);
  },
  endTrackingRequest: (id: string) => {
    eventHub.emit(EventNames.trackingRequestFinished, id);
  },
});

export default eventHub;
