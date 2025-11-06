import { useRouter } from "next/router";
import { JobDetail } from "src/components/JobDetail/JobDetail";
import { PageContainer } from "src/components/Layout/PageContainer";

export default function JobDetailPage() {
  const router = useRouter();
  const id = typeof router.query.id === "string" ? router.query.id : undefined;
  if (!id) return null;
  return (
    <PageContainer>
      <JobDetail id={id} />
    </PageContainer>
  );
}
