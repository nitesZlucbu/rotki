import i18n from '@/i18n';
import {
  BalanceSnapshotError,
  SocketMessageType,
  WebsocketMessage
} from '@/services/websocket/messages';
import { Severity } from '@/store/notifications/consts';
import { userNotify } from '@/store/notifications/utils';

export async function handleSnapshotError(
  message: WebsocketMessage<SocketMessageType>
) {
  const data = BalanceSnapshotError.parse(message.data);
  await userNotify({
    title: i18n.t('notification_messages.snapshot_failed.title').toString(),
    message: i18n
      .t('notification_messages.snapshot_failed.message', data)
      .toString(),
    display: true
  });
}

export async function handleLegacyMessage(message: string, isWarning: boolean) {
  await userNotify({
    title: i18n.t('notification_messages.backend.title').toString(),
    message: message,
    display: !isWarning,
    severity: isWarning ? Severity.WARNING : Severity.ERROR
  });
}