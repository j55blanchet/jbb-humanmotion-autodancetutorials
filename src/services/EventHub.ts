import { TinyEmitter } from 'tiny-emitter';

export const EventNames = Object.freeze({
  gesture: 'gesture',
});

export const Gestures = Object.freeze({
  none: 'none',
  pointLeft: 'point-left',
  pointRight: 'point-right',
});

const eventHub = new TinyEmitter();

export default eventHub;
