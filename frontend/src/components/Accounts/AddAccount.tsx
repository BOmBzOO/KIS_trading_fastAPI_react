import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"

import { type AccountCreate, AccountsService, type ApiError } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddAccount = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<AccountCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      acnt_name: "",
      cano: "",
      acnt_prdt_cd: "",
      acnt_type: "",
      hts_id: "",
      is_active: true,
      app_key: "",
      app_secret: "",
      discord_webhook_url: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: AccountCreate) =>
      AccountsService.createAccount({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("계좌가 성공적으로 생성되었습니다.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] })
    },
  })

  const onSubmit: SubmitHandler<AccountCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-account" my={4}>
          <FaPlus fontSize="16px" />
          계좌 추가
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>계좌 추가</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>새 계좌 정보를 입력해주세요.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.acnt_name}
                errorText={errors.acnt_name?.message}
                label="계좌명"
              >
                <Input
                  id="acnt_name"
                  {...register("acnt_name", {
                    required: "계좌명은 필수입니다.",
                  })}
                  placeholder="계좌명"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.cano}
                errorText={errors.cano?.message}
                label="계좌번호"
              >
                <Input
                  id="cano"
                  {...register("cano", {
                    required: "계좌번호는 필수입니다.",
                  })}
                  placeholder="계좌번호"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.acnt_prdt_cd}
                errorText={errors.acnt_prdt_cd?.message}
                label="상품코드"
              >
                <Input
                  id="acnt_prdt_cd"
                  {...register("acnt_prdt_cd", {
                    required: "상품코드는 필수입니다.",
                  })}
                  placeholder="상품코드"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.acnt_type}
                errorText={errors.acnt_type?.message}
                label="계좌유형"
              >
                <Input
                  id="acnt_type"
                  {...register("acnt_type", {
                    required: "계좌유형은 필수입니다.",
                  })}
                  placeholder="계좌유형"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.hts_id}
                errorText={errors.hts_id?.message}
                label="HTS ID"
              >
                <Input
                  id="hts_id"
                  {...register("hts_id", {
                    required: "HTS ID는 필수입니다.",
                  })}
                  placeholder="HTS ID"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.app_key}
                errorText={errors.app_key?.message}
                label="App Key"
              >
                <Input
                  id="app_key"
                  {...register("app_key", {
                    required: "App Key는 필수입니다.",
                  })}
                  placeholder="App Key"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.app_secret}
                errorText={errors.app_secret?.message}
                label="App Secret"
              >
                <Input
                  id="app_secret"
                  {...register("app_secret", {
                    required: "App Secret는 필수입니다.",
                  })}
                  placeholder="App Secret"
                  type="password"
                />
              </Field>

              <Field
                invalid={!!errors.discord_webhook_url}
                errorText={errors.discord_webhook_url?.message}
                label="Discord Webhook URL"
              >
                <Input
                  id="discord_webhook_url"
                  {...register("discord_webhook_url")}
                  placeholder="Discord Webhook URL"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                취소
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              저장
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddAccount 