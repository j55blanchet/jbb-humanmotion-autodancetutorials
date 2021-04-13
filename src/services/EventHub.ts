import { TinyEmitter } from 'tiny-emitter';
import { onMounted, onBeforeUnmount } from 'vue';
import { MpHolisticResults } from './MediaPipeTypes';

export const EventNames = Object.freeze({
  gesture: 'gesture',
  trackingResults: 'trackingResults',
  trackingRequested: 'trackingRequested',
  trackingRequestFinished: 'trackingRequestFinished',
});

export const GestureNames = Object.freeze({
  none: 'none',
  pointLeft: 'point-left',
  pointRight: 'point-right',
});

const eventHub = new TinyEmitter();

export function setupGestureListening(callbacks: Record<string, () => void>) {
  function onGesture(gesture: string) {
    const cb = callbacks[gesture];
    if (cb) cb();
  }
  onMounted(() => {
    eventHub.on(EventNames.gesture, onGesture);
  });
  onBeforeUnmount(() => {
    eventHub.off(EventNames.gesture, onGesture);
  });
}

export function setupMediaPipeListening(callback: (res: MpHolisticResults) => void) {

  onMounted(() => {
    eventHub.on(EventNames.trackingResults, callback);
  });
  onBeforeUnmount(() => {
    eventHub.off(EventNames.trackingResults, callback);
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
