"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { login, fetchMe } from "@/lib/axios";
import { useApiError } from "@/hooks/use-api-error";
import { useAuthStore } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Card, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorMessage } from "@/components/ui/error-message";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login: loginStore } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const { error, details: errorDetails, setError: setApiError, reset: resetApiError } = useApiError();

  const onSubmit = async (data: LoginForm) => {
    try {
      resetApiError();
      await login(data.email, data.password);
      const user = await fetchMe();
      loginStore(user);
      router.push("/dashboard");
    } catch (err) {
      setApiError(err);
    }
  };

  return (
    <Card className="w-full max-w-md border-none bg-transparent shadow-none">
      <CardTitle className="text-2xl">Welcome back</CardTitle>
      <p className="mt-2 text-sm text-muted-foreground">
        Sign in to continue your learning journey
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        {error && <ErrorMessage details={errorDetails}>{error}</ErrorMessage>}

        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" {...register("email")} className="mt-1" />
          {errors.email && <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>}
        </div>

        <div>
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" {...register("password")} className="mt-1" />
          {errors.password && <p className="mt-1 text-xs text-destructive">{errors.password.message}</p>}
        </div>

        <Button type="submit" loading={isSubmitting} className="w-full">
          Sign in
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-semibold text-primary hover:underline">
          Register
        </Link>
      </p>
    </Card>
  );
}
