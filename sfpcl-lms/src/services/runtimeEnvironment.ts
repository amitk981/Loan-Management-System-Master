export const DEMO_SURFACES_ENABLED = (
  !import.meta.env.PROD
  && import.meta.env.VITE_ENABLE_DEMO_SURFACES !== 'false'
);
