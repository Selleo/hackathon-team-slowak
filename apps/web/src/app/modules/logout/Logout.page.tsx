import { Card, CardContent, CardHeader } from "@/components/ui/card.tsx";
import { Avatar, AvatarImage } from "@/components/ui/avatar.tsx";
import { FieldLegend, FieldSet } from "@/components/ui/field.tsx";

export const LogoutPage = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <Card>
        <CardHeader className="justify-center">
          <Avatar className="size-16 aspect-square">
            <AvatarImage src="/logo.png" />
          </Avatar>
        </CardHeader>
        <CardContent>
          <FieldSet>
            <FieldLegend className="w-full text-center animate-pulse">
              Logging out...
            </FieldLegend>
          </FieldSet>
        </CardContent>
      </Card>
    </div>
  );
};
