// types/plugins.d.ts
declare module '#app' {
  interface NuxtApp {
    $googleSignIn: {
      signIn: () => Promise<{ credential: string }>;
      isLoaded: { value: boolean };
    }
  }
}

export {}