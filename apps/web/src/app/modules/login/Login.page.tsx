import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import {
  Field,
  FieldError,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "@/components/ui/field.tsx";
import { Link } from "react-router-dom";
import { Avatar, AvatarImage } from "@/components/ui/avatar.tsx";
import useLoginUser from "@/app/api/mutations/useLoginUser.ts";

const loginSchema = z.object({
  email: z.email("Invalid email address"),
  password: z.string().min(1, "Username is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginPage = () => {
  const { mutateAsync: loginUser } = useLoginUser();

  const {
    register,
    handleSubmit,
    formState: { errors, isLoading },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    await loginUser(data);
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <Card className="w-full max-w-md">
        <CardHeader className="justify-center">
          <Avatar className="size-16 aspect-square">
            <AvatarImage src="/logo.png" />
          </Avatar>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <FieldSet>
              <FieldLegend className="w-full text-center">
                Login to your account
              </FieldLegend>
              <Field>
                <FieldLabel htmlFor="email">Email</FieldLabel>
                <Input
                  id="email"
                  type="email"
                  placeholder="example@luma.com"
                  {...register("email")}
                />
                {errors.email && (
                  <FieldError>{errors.email.message}</FieldError>
                )}
              </Field>
              <Field>
                <FieldLabel htmlFor="password">Password</FieldLabel>
                <Input
                  id="password"
                  type="password"
                  placeholder="********"
                  {...register("password")}
                />
                {errors.password && (
                  <FieldError>{errors.password.message}</FieldError>
                )}
              </Field>
              <Field>
                <Button disabled={isLoading} variant="default" type="submit">
                  Login
                </Button>
              </Field>
            </FieldSet>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center text-center">
          <span className="text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link to="/register" className="underline">
              Sign up
            </Link>
          </span>
        </CardFooter>
      </Card>
    </div>
  );
};
